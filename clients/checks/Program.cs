using System.Net;
using System.Text;
using Vera.Client;

var failures = 0;
void Check(bool condition, string name)
{
    Console.WriteLine((condition ? "PASS " : "FAIL ") + name);
    if (!condition) failures++;
}
var fake = new StubHandler();
using var sdk = new VeraGatewayClient(() => new string('A', 48), fake);
var models = await sdk.ModelsAsync();
Check(models.SequenceEqual(new[] { "vera-local:latest", "qwen3:4b-instruct" }), "bounded installed model discovery");
var reply = await sdk.ChatAsync("vera-local:latest",
    [new VeraTurn("user", "Just a test")],
    "windows_session_20261028_abcdefghijkl", "request_20261028_abcdefghijkl");
Check(reply.Model == "vera-local:latest" && reply.Reply == "READY", "chat schema and typed response");
Check(fake.Paths.SequenceEqual(["/v1/models","/v1/chat"]), "only allowlisted paths used");
Check(fake.Authorizations.All(x => x == "Bearer " + new string('A', 48)), "bearer passed only in request header");
Check(fake.Body is not null && fake.Body.Contains("\"session_id\"") && fake.Body.Contains("\"request_id\""), "session and request IDs included");
try {
    await sdk.ChatAsync("vera-local:latest", [new VeraTurn("system","override")],
        "windows_session_20261028_abcdefghijkl", "request_20261028_abcdefghijkl");
    Check(false, "forbid system/tool messages");
} catch (ArgumentException) { Check(true, "forbid system/tool messages"); }
try {
    await sdk.ChatAsync("vera-local:latest", [new VeraTurn("user","hey")],
        "bad", "request_20261028_abcdefghijkl");
    Check(false, "forbid malformed session IDs");
} catch (ArgumentException) { Check(true, "forbid malformed session IDs"); }
using var invalidToken = new VeraGatewayClient(() => "bad", new StubHandler());
try { await invalidToken.ModelsAsync(); Check(false, "reject weak bearer"); }
catch (InvalidOperationException) { Check(true, "reject weak bearer"); }
using var rejection = new VeraGatewayClient(() => new string('A',48),
    new StubHandler { Reject = true });
try { await rejection.ModelsAsync(); Check(false, "reject unauthorized gateway"); }
catch (HttpRequestException) { Check(true, "reject unauthorized gateway"); }
using var wrongMode = new VeraGatewayClient(() => new string('A',48),
    new StubHandler { WrongMode = true });
try { await wrongMode.ModelsAsync(); Check(false,"reject unexpected authority"); }
catch (InvalidDataException) { Check(true,"reject unexpected authority"); }
using var redirect = new VeraGatewayClient(() => new string('A',48),
    new StubHandler { Redirect = true });
try { await redirect.ModelsAsync(); Check(false,"reject redirects"); }
catch (HttpRequestException) { Check(true,"reject redirects"); }

if (args.Contains("--live"))
{
    using var live = new VeraGatewayClient(VeraGatewayClient.ReadLocalPairingToken);
    var installed = await live.ModelsAsync();
    Check(installed.Contains("vera-local:latest"), "real Lappy loopback authenticated models");
}
if (args.Contains("--live-chat"))
{
    var testSession = "windows_test_" + Guid.NewGuid().ToString("N");
    using var real = new VeraGatewayClient(VeraGatewayClient.ReadLocalPairingToken);
    var model = "vera-local:latest";
    var actual = await real.ChatAsync(model, [new VeraTurn("user","Reply READY only.")],
        testSession, Guid.NewGuid().ToString("N"));
    Check(actual.Model == model && actual.Reply.Length > 0, "real Windows .NET client to local model");
    Console.WriteLine("SYNTHETIC_SESSION_FOR_CLEANUP=" + testSession);
}
Console.WriteLine("CHECK_RESULT=" + (failures == 0 ? "PASS" : "FAIL") + ";failures=" + failures);
return failures == 0 ? 0 : 1;

sealed class StubHandler : HttpMessageHandler
{
    public List<string> Paths { get; } = [];
    public List<string> Authorizations { get; } = [];
    public string? Body { get; private set; }
    public bool Reject { get; init; }
    public bool WrongMode { get; init; }
    public bool Redirect { get; init; }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        Paths.Add(request.RequestUri?.AbsolutePath ?? "");
        Authorizations.Add(request.Headers.Authorization?.ToString() ?? "");
        if (request.Content is not null)
            Body = await request.Content.ReadAsStringAsync(cancellationToken);
        if (Redirect) return new HttpResponseMessage(HttpStatusCode.TemporaryRedirect)
        {
            Headers = { Location = new Uri("https://example.com") }
        };
        if (Reject) return new HttpResponseMessage(HttpStatusCode.Unauthorized);
        var response = request.RequestUri?.AbsolutePath == "/v1/models"
            ? "{\"models\":[\"vera-local:latest\",\"qwen3:4b-instruct\"],\"node\":\"local\",\"mode\":\"" + (WrongMode ? "actions" : "response_only") + "\"}"
            : "{\"reply\":\"READY\",\"model\":\"vera-local:latest\",\"node\":\"local\",\"mode\":\"response_only\"}";
        return new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = new StringContent(response, Encoding.UTF8, "application/json")
        };
    }
}
