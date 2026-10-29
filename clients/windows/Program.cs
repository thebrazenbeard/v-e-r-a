using System.Drawing;
using System.Windows.Forms;
using Vera.Client;

namespace Vera.Desktop;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        ApplicationConfiguration.Initialize();
        Application.Run(new VeraWindow());
    }
}

/// <summary>WinForms native feasibility client sharing the exact phone gateway+STM.</summary>
public sealed class VeraWindow : Form
{
    private static readonly Color Night = Color.FromArgb(21, 13, 27);
    private static readonly Color Panel = Color.FromArgb(43, 22, 43);
    private static readonly Color Rose = Color.FromArgb(237, 171, 196);
    private static readonly Color Light = Color.FromArgb(250, 237, 245);

    private readonly VeraGatewayClient _gateway = new(VeraGatewayClient.ReadLocalPairingToken);
    private readonly List<VeraTurn> _history = [];
    private readonly string _sessionId = LoadSessionId();
    private readonly RichTextBox _chat = new() { ReadOnly = true, BorderStyle = BorderStyle.None };
    private readonly TextBox _composer = new() { Multiline = true, AcceptsReturn = true, ScrollBars = ScrollBars.Vertical };
    private readonly ComboBox _models = new() { DropDownStyle = ComboBoxStyle.DropDownList };
    private readonly Button _connect = new() { Text = "Connect" };
    private readonly Button _send = new() { Text = "Send" };
    private readonly Label _status = new() { Text = "Private local inference · disconnected" };
    private bool _busy;
    private bool _connected;

    public VeraWindow()
    {
        Text = "Vera Desktop  ·  Local Inference";
        Width = 920;
        Height = 700;
        MinimumSize = new Size(560, 430);
        StartPosition = FormStartPosition.CenterScreen;
        BackColor = Night;
        ForeColor = Light;
        Font = new Font("Segoe UI", 11F);
        var ico = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "VeraPhoneGateway", "vera_interface.ico");
        if (File.Exists(ico))
        {
            try { Icon = new Icon(ico); } catch (ArgumentException) { /* optional */ }
        }
        var root = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 1,
            RowCount = 4,
            Padding = new Padding(22)
        };
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 73));
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 76));
        root.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        root.RowStyles.Add(new RowStyle(SizeType.Absolute, 115));
        Controls.Add(root);

        var brand = new Label
        {
            Text = "V E R A    /    DESKTOP",
            Font = new Font("Georgia", 27F, FontStyle.Regular),
            ForeColor = Rose, Dock = DockStyle.Fill,
            TextAlign = ContentAlignment.MiddleLeft
        };
        root.Controls.Add(brand, 0, 0);

        var bar = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 3, RowCount = 2 };
        bar.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        bar.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 115));
        bar.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 115));
        bar.RowStyles.Add(new RowStyle(SizeType.Absolute, 43));
        bar.RowStyles.Add(new RowStyle(SizeType.Absolute, 29));
        _models.BackColor = Panel;
        _models.ForeColor = Light;
        _models.Dock = DockStyle.Fill;
        _models.FlatStyle = FlatStyle.Flat;
        _models.Font = new Font("Segoe UI", 11F);
        bar.Controls.Add(_models, 0, 0);
        StyleButton(_connect);
        _connect.Dock = DockStyle.Fill;
        bar.Controls.Add(_connect, 1, 0);
        var privacy = new Label
        {
            Text = "Local only  ·  Response only",
            ForeColor = Rose,
            TextAlign = ContentAlignment.MiddleCenter,
            Dock = DockStyle.Fill,
            Font = new Font("Segoe UI", 9F)
        };
        bar.Controls.Add(privacy, 2, 0);
        _status.Dock = DockStyle.Fill;
        _status.ForeColor = Rose;
        _status.Font = new Font("Segoe UI", 9F);
        bar.SetColumnSpan(_status, 3);
        bar.Controls.Add(_status, 0, 1);
        root.Controls.Add(bar, 0, 1);

        _chat.Dock = DockStyle.Fill;
        _chat.BackColor = Panel;
        _chat.ForeColor = Light;
        _chat.Font = new Font("Segoe UI", 12F);
        _chat.Padding = new Padding(8);
        _chat.DetectUrls = false;
        _chat.TabStop = false;
        root.Controls.Add(_chat, 0, 2);

        var bottom = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2 };
        bottom.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        bottom.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 111));
        _composer.Dock = DockStyle.Fill;
        _composer.BackColor = Panel;
        _composer.ForeColor = Light;
        _composer.BorderStyle = BorderStyle.FixedSingle;
        _composer.Font = new Font("Segoe UI", 12F);
        _composer.PlaceholderText = "Message Vera…";
        _composer.KeyDown += (s, e) =>
        {
            if (e.Control && e.KeyCode == Keys.Enter) { e.SuppressKeyPress = true; _ = SendAsync(); }
        };
        bottom.Controls.Add(_composer, 0, 0);
        StyleButton(_send);
        _send.Dock = DockStyle.Fill;
        bottom.Controls.Add(_send, 1, 0);
        root.Controls.Add(bottom, 0, 3);

        _connect.Click += async (_, _) => await ConnectAsync();
        _send.Click += async (_, _) => await SendAsync();
        UpdateControls();
        Append("VERA", "Private local inference uses the same loopback gateway and encrypted STM journal as Vera Companion.\nPress Connect. Ctrl+Enter sends a message.");
        Shown += async (_, _) => await ConnectAsync();
        FormClosed += (_, _) => _gateway.Dispose();
    }

    private static void StyleButton(Button button)
    {
        button.FlatStyle = FlatStyle.Flat;
        button.FlatAppearance.BorderColor = Rose;
        button.BackColor = Color.FromArgb(112, 44, 78);
        button.ForeColor = Color.White;
        button.Font = new Font("Segoe UI Semibold", 10F);
    }

    private static string LoadSessionId()
    {
        var folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "VeraDesktop");
        Directory.CreateDirectory(folder);
        var path = Path.Combine(folder, "conversation-id.txt");
        if (File.Exists(path))
        {
            var current = File.ReadAllText(path).Trim();
            if (current.Length == 32 && current.All(Uri.IsHexDigit)) return current;
        }
        var result = Guid.NewGuid().ToString("N");
        File.WriteAllText(path, result);
        return result;
    }

    private void UpdateControls()
    {
        _connect.Enabled = !_busy;
        _send.Enabled = !_busy && _connected && _models.SelectedItem != null;
        _composer.Enabled = !_busy || !_connected;
    }

    private void Append(string speaker, string content)
    {
        _chat.SelectionStart = _chat.TextLength;
        _chat.SelectionColor = Rose;
        _chat.SelectionFont = new Font("Segoe UI Semibold", 11F);
        _chat.AppendText("\n" + speaker.ToUpperInvariant() + "\n");
        _chat.SelectionColor = Light;
        _chat.SelectionFont = new Font("Segoe UI", 12F);
        _chat.AppendText(content + "\n");
        _chat.SelectionStart = _chat.TextLength;
        _chat.ScrollToCaret();
    }

    private async Task ConnectAsync()
    {
        if (_busy) return;
        _busy = true;
        _status.Text = "Checking local Vera gateway…";
        UpdateControls();
        try
        {
            var previous = _models.SelectedItem as string;
            var installed = await _gateway.ModelsAsync();
            if (installed.Count == 0) throw new InvalidDataException("No installed models.");
            _models.Items.Clear();
            foreach (var model in installed) _models.Items.Add(model);
            var preferred = installed.Contains(previous) ? previous
                : installed.Contains("vera-local:latest") ? "vera-local:latest" : installed[0];
            _models.SelectedItem = preferred;
            _connected = true;
            _status.Text = "Connected · " + installed.Count + " local models · encrypted STM enabled when gateway journal configured";
        }
        catch (Exception ex)
        {
            _connected = false;
            _status.Text = "Could not connect · " + ex.GetType().Name + " (check local gateway)";
        }
        finally { _busy = false; UpdateControls(); }
    }

    private async Task SendAsync()
    {
        if (_busy || !_connected || _models.SelectedItem is not string model) return;
        var prompt = _composer.Text.Trim();
        if (prompt.Length == 0 || prompt.Length > 4096)
        {
            _status.Text = "Message must contain 1–4096 characters";
            return;
        }
        var requestId = Guid.NewGuid().ToString("N");
        var request = _history.TakeLast(10).Append(new VeraTurn("user",prompt)).ToList();
        _busy = true;
        _composer.Clear();
        Append("YOU", prompt);
        _status.Text = "Generating with " + model + "…";
        UpdateControls();
        try
        {
            var result = await _gateway.ChatAsync(model, request, _sessionId, requestId);
            _history.Add(new VeraTurn("user", prompt));
            _history.Add(new VeraTurn("assistant", result.Reply));
            Append("VERA  ·  " + result.Model, result.Reply);
            _status.Text = "Connected · " + result.Model + " · response only";
        }
        catch (Exception ex)
        {
            if (_composer.Text.Length == 0) _composer.Text = prompt;
            Append("SYSTEM", "Message not delivered. Draft restored.");
            _status.Text = "Request failed: " + ex.GetType().Name + "; connection can be retried";
        }
        finally { _busy = false; UpdateControls(); }
    }
}
