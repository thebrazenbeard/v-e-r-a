import { sha256Hex } from "./crypto.ts";
import { auditReports } from "./evidence.ts";
import { OpenAICompatibleModel } from "./llm.ts";
import { reconcile } from "./reconcile.ts";
import { skepticFlags } from "./skeptic.ts";
import type { ReviewContext, ReviewReport } from "./types.ts";
import type { Settings } from "./config.ts";

export async function reviewIdFor(
  context: ReviewContext,
  settings: Settings,
): Promise<string> {
  const subject = context.subject;
  const contextDigest = await sha256Hex(new TextEncoder().encode(context.text));
  const raw = [
    settings.reviewProtocolVersion,
    subject.repository,
    subject.kind,
    subject.number ?? "",
    subject.base_sha ?? "",
    subject.head_sha,
    settings.masaProviderId,
    settings.masaModel,
    settings.muneProviderId,
    settings.muneModel,
    contextDigest,
  ].join("|");
  return (await sha256Hex(new TextEncoder().encode(raw))).slice(0, 24);
}

export class MasamuneOrchestrator {
  readonly masa: OpenAICompatibleModel;
  readonly mune: OpenAICompatibleModel;

  constructor(private readonly settings: Settings) {
    this.masa = new OpenAICompatibleModel({
      baseUrl: settings.masaBaseUrl,
      apiKey: settings.masaApiKey,
      providerId: settings.masaProviderId,
      modelId: settings.masaModel,
      timeoutMs: settings.requestTimeoutMs,
      maxOutputTokens: settings.modelMaxOutputTokens,
      repairInvalidJson: false,
    });
    this.mune = new OpenAICompatibleModel({
      baseUrl: settings.muneBaseUrl,
      apiKey: settings.muneApiKey,
      providerId: settings.muneProviderId,
      modelId: settings.muneModel,
      timeoutMs: settings.requestTimeoutMs,
      maxOutputTokens: settings.modelMaxOutputTokens,
      repairInvalidJson: true,
    });
  }

  async review(context: ReviewContext): Promise<ReviewReport> {
    const [masaReport, muneBlind] = await Promise.all([
      this.masa.masaScan(context.text),
      this.mune.muneBlindScan(context.text),
    ]);

    const challenges = await this.mune.muneChallenge(
      context.text,
      muneBlind,
      masaReport,
    );

    const evidenceReceipts = await auditReports(
      masaReport,
      muneBlind,
      context.text,
    );

    const scopeNote =
      `Bounded zero-cost review: at most ${context.policy.max_files} selected files, ` +
      `${context.policy.max_file_bytes} UTF-8 bytes per file/patch, and ` +
      `${context.policy.max_context_bytes} UTF-8 bytes of aggregate source/diff context. ` +
      "A missing finding is not evidence of absence.";

    const flags = skepticFlags(
      masaReport,
      muneBlind,
      challenges,
      evidenceReceipts,
    );
    const report = reconcile(
      context.subject,
      masaReport,
      muneBlind,
      challenges,
      evidenceReceipts,
      scopeNote,
    );
    return { ...report, skeptic_flags: flags };
  }
}
