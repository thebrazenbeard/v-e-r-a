using System.Net;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Vera.Client;

/// <summary>Only bounded response-only requests to the locally installed Vera gateway.</summary>
public sealed class VeraGatewayClient : IDisposable
{
    public const string GatewayUrl = "http://127.0.0.1:18777/";
    private readonly HttpClient _http;
    private readonly Func<string> _token;
    private static readonly Regex Identifier = new("^[A-Za-z0-9_-]{16,128}$", RegexOptions.CultureInvariant);
    private static readonly Regex Bearer = new("^[A-Za-z0-9_-]{32,128}$", RegexOptions.CultureInvariant);

    public VeraGatewayClient(Func<string> pairingToken, HttpMessageHandler? handler = null)
    {
        _token = pairingToken ?? throw new ArgumentNullException(nameof(pairingToken));
        _http = new HttpClient(handler ?? new SocketsHttpHandler
        {
            AllowAutoRedirect = false,
            UseProxy = false,
            ConnectTimeout = TimeSpan.FromSeconds(10)
        })
        {
            BaseAddress = new Uri(GatewayUrl),
            Timeout = TimeSpan.FromSeconds(100),
            MaxResponseContentBufferSize = 65536
        };
    }

    public static string ReadLocalPairingToken()
    {
        var path = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "VeraPhoneGateway", "pairing-token.txt");
        return File.ReadAllText(path, Encoding.ASCII).Trim();
    }

    public async Task<IReadOnlyList<string>> ModelsAsync(CancellationToken ct = default)
    {
        using var doc = await SendAsync(HttpMethod.Get, "v1/models", null, ct);
        var root = doc.RootElement;
        if (root.GetProperty("mode").GetString() != "response_only"
            || root.GetProperty("node").GetString() != "local")
            throw new InvalidDataException("Unexpected gateway response authority.");
        var models = root.GetProperty("models");
        if (models.ValueKind != JsonValueKind.Array || models.GetArrayLength() > 32)
            throw new InvalidDataException("Unbounded model inventory.");
        var result = new List<string>();
        foreach (var item in models.EnumerateArray())
        {
            var name = item.GetString();
            if (string.IsNullOrEmpty(name) || name.Length > 128)
                throw new InvalidDataException("Invalid installed model name.");
            result.Add(name);
        }
        return result;
    }

    public async Task<VeraAnswer> ChatAsync(string model, IReadOnlyList<VeraTurn> turns,
        string sessionId, string requestId, CancellationToken ct = default)
    {
        if (!Identifier.IsMatch(sessionId) || !Identifier.IsMatch(requestId))
            throw new ArgumentException("Invalid opaque session or request identifier.");
        if (model is null || model.Length is < 1 or > 128)
            throw new ArgumentException("Invalid model.");
        if (turns.Count is < 1 or > 12 || turns[^1].Role != "user")
            throw new ArgumentException("Invalid chat history.");
        foreach (var turn in turns)
        {
            if ((turn.Role != "user" && turn.Role != "assistant") ||
                turn.Content is null || turn.Content.Length is < 1 or > 4096)
                throw new ArgumentException("Only bounded user and assistant messages are permitted.");
        }

        var payload = JsonSerializer.Serialize(new
        {
            model,
            messages = turns.Select(t => new { role = t.Role, content = t.Content }),
            session_id = sessionId,
            request_id = requestId
        });
        if (Encoding.UTF8.GetByteCount(payload) > 32768)
            throw new ArgumentException("Chat payload exceeds gateway limit.");
        using var doc = await SendAsync(HttpMethod.Post, "v1/chat", payload, ct);
        var root = doc.RootElement;
        if (root.GetProperty("mode").GetString() != "response_only"
            || root.GetProperty("node").GetString() != "local")
            throw new InvalidDataException("Gateway granted unexpected authority.");
        var answer = root.GetProperty("reply").GetString();
        var answeredBy = root.GetProperty("model").GetString();
        if (string.IsNullOrEmpty(answer) || answer.Length > 16000
            || answeredBy != model)
            throw new InvalidDataException("Invalid or mismatched model response.");
        return new VeraAnswer(answeredBy, answer);
    }

    private async Task<JsonDocument> SendAsync(HttpMethod method, string path, string? payload,
        CancellationToken ct)
    {
        var token = _token();
        if (token == null || !Bearer.IsMatch(token))
            throw new InvalidOperationException("Local Vera pairing file missing or invalid.");
        using var req = new HttpRequestMessage(method, path);
        req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        req.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        if (payload != null)
            req.Content = new StringContent(payload, Encoding.UTF8, "application/json");
        using var response = await _http.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct);
        if (response.StatusCode != HttpStatusCode.OK)
            throw new HttpRequestException("Local Vera gateway returned HTTP " + (int)response.StatusCode);
        var media = response.Content.Headers.ContentType?.MediaType;
        if (media != "application/json")
            throw new InvalidDataException("Unexpected gateway content type.");
        if (response.Content.Headers.ContentLength > 65536)
            throw new InvalidDataException("Gateway response exceeds bound.");
        await using var stream = await response.Content.ReadAsStreamAsync(ct);
        using var collected = new MemoryStream();
        var buffer = new byte[4096];
        int count;
        while ((count = await stream.ReadAsync(buffer, ct)) != 0)
        {
            if (collected.Length + count > 65536)
                throw new InvalidDataException("Gateway response exceeds bound.");
            collected.Write(buffer, 0, count);
        }
        collected.Position = 0;
        return await JsonDocument.ParseAsync(collected, cancellationToken: ct);
    }

    public void Dispose() => _http.Dispose();
}

public sealed record VeraTurn(string Role, string Content);
public sealed record VeraAnswer(string Model, string Reply);
