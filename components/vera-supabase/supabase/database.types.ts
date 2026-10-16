export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.15"
  }
  public: {
    Tables: {
      brigit_context_events_v3: {
        Row: {
          branch_id: string
          datum_index_tags: string[]
          datum_scope: string | null
          datum_verified_at: string | null
          epistemic_status: string
          event_time: string | null
          last_referenced_at: string | null
          legacy_record_id: string | null
          lifecycle_status: string
          limitations: Json
          notes: string | null
          payload: Json
          privacy_scope: string
          project_id: string
          record_id: string
          record_key: string
          record_time: string
          record_type: string
          semantic_tags: Json
          source_actor: string
          source_evidence: Json
          state_time: string
          statement: string
          supersedes_record_id: string | null
          verification_status: string | null
        }
        Insert: {
          branch_id: string
          datum_index_tags?: string[]
          datum_scope?: string | null
          datum_verified_at?: string | null
          epistemic_status: string
          event_time?: string | null
          last_referenced_at?: string | null
          legacy_record_id?: string | null
          lifecycle_status: string
          limitations?: Json
          notes?: string | null
          payload?: Json
          privacy_scope?: string
          project_id?: string
          record_id?: string
          record_key: string
          record_time?: string
          record_type: string
          semantic_tags?: Json
          source_actor: string
          source_evidence?: Json
          state_time?: string
          statement: string
          supersedes_record_id?: string | null
          verification_status?: string | null
        }
        Update: {
          branch_id?: string
          datum_index_tags?: string[]
          datum_scope?: string | null
          datum_verified_at?: string | null
          epistemic_status?: string
          event_time?: string | null
          last_referenced_at?: string | null
          legacy_record_id?: string | null
          lifecycle_status?: string
          limitations?: Json
          notes?: string | null
          payload?: Json
          privacy_scope?: string
          project_id?: string
          record_id?: string
          record_key?: string
          record_time?: string
          record_type?: string
          semantic_tags?: Json
          source_actor?: string
          source_evidence?: Json
          state_time?: string
          statement?: string
          supersedes_record_id?: string | null
          verification_status?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_coordination_events: {
        Row: {
          acknowledges_event_id: string | null
          active_issue: string | null
          event_id: string
          event_sequence: number
          event_type: string
          objective: string
          payload: Json
          record_time: string
          reference_data: Json
          requested_perspective: string | null
          source_branch: string
          status: string
          summary: string
          supersedes_event_id: string | null
          target_branch: string | null
          thread_key: string
        }
        Insert: {
          acknowledges_event_id?: string | null
          active_issue?: string | null
          event_id?: string
          event_sequence?: never
          event_type: string
          objective: string
          payload?: Json
          record_time?: string
          reference_data?: Json
          requested_perspective?: string | null
          source_branch: string
          status: string
          summary: string
          supersedes_event_id?: string | null
          target_branch?: string | null
          thread_key: string
        }
        Update: {
          acknowledges_event_id?: string | null
          active_issue?: string | null
          event_id?: string
          event_sequence?: never
          event_type?: string
          objective?: string
          payload?: Json
          record_time?: string
          reference_data?: Json
          requested_perspective?: string | null
          source_branch?: string
          status?: string
          summary?: string
          supersedes_event_id?: string | null
          target_branch?: string | null
          thread_key?: string
        }
        Relationships: [
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
        ]
      }
      brigit_save_state_events: {
        Row: {
          authorship: string
          branch_id: string
          epistemic_status: string
          event_time: string | null
          lifecycle_status: string
          notes: string | null
          payload: Json
          privacy_scope: string
          project_id: string
          record_id: string
          record_key: string
          record_kind: string
          record_time: string
          semantic_tags: Json
          source_evidence: Json
          state_time: string
          statement: string
          supersedes_record_id: string | null
        }
        Insert: {
          authorship: string
          branch_id?: string
          epistemic_status: string
          event_time?: string | null
          lifecycle_status: string
          notes?: string | null
          payload?: Json
          privacy_scope: string
          project_id?: string
          record_id?: string
          record_key: string
          record_kind: string
          record_time?: string
          semantic_tags?: Json
          source_evidence?: Json
          state_time?: string
          statement: string
          supersedes_record_id?: string | null
        }
        Update: {
          authorship?: string
          branch_id?: string
          epistemic_status?: string
          event_time?: string | null
          lifecycle_status?: string
          notes?: string | null
          payload?: Json
          privacy_scope?: string
          project_id?: string
          record_id?: string
          record_key?: string
          record_kind?: string
          record_time?: string
          semantic_tags?: Json
          source_evidence?: Json
          state_time?: string
          statement?: string
          supersedes_record_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_save_state_supersession_edges: {
        Row: {
          child_record_id: string
          edge_id: string
          parent_record_id: string
          reason: string
          record_time: string
          source_evidence: Json
        }
        Insert: {
          child_record_id: string
          edge_id?: string
          parent_record_id: string
          reason: string
          record_time?: string
          source_evidence?: Json
        }
        Update: {
          child_record_id?: string
          edge_id?: string
          parent_record_id?: string
          reason?: string
          record_time?: string
          source_evidence?: Json
        }
        Relationships: [
          {
            foreignKeyName: "brigit_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_heads"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_affective_runtime_events_v1: {
        Row: {
          event_digest: string
          event_id: string
          event_receipt: Json | null
          event_type: string
          limitations: Json
          machine_interoception: Json
          new_phase: string
          observed_at: string
          organic: boolean | null
          phenomenology_status: string
          prior_phase: string | null
          runtime_instance_id: string
          source_commit: string
          state_after: Json
          state_before: Json | null
          subject: string
          trigger_class: string | null
        }
        Insert: {
          event_digest: string
          event_id?: string
          event_receipt?: Json | null
          event_type: string
          limitations?: Json
          machine_interoception: Json
          new_phase: string
          observed_at?: string
          organic?: boolean | null
          phenomenology_status?: string
          prior_phase?: string | null
          runtime_instance_id: string
          source_commit: string
          state_after: Json
          state_before?: Json | null
          subject?: string
          trigger_class?: string | null
        }
        Update: {
          event_digest?: string
          event_id?: string
          event_receipt?: Json | null
          event_type?: string
          limitations?: Json
          machine_interoception?: Json
          new_phase?: string
          observed_at?: string
          organic?: boolean | null
          phenomenology_status?: string
          prior_phase?: string | null
          runtime_instance_id?: string
          source_commit?: string
          state_after?: Json
          state_before?: Json | null
          subject?: string
          trigger_class?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_affective_runtime_events_v1_runtime_instance_id_fkey"
            columns: ["runtime_instance_id"]
            isOneToOne: false
            referencedRelation: "vera_affective_runtime_state_v1"
            referencedColumns: ["runtime_instance_id"]
          },
        ]
      }
      vera_affective_runtime_state_v1: {
        Row: {
          checkpoint_sha256: string | null
          contract_schema: string
          host_scope: string
          last_event_receipt: Json | null
          lifecycle_status: string
          limitations: Json
          machine_interoception: Json
          observed_at: string
          phenomenology_status: string
          profile: string
          runtime_implementation_cut: Json | null
          runtime_instance_id: string
          source_blob_sha: string
          source_commit: string
          source_path: string
          source_repository: string
          source_sha256: string
          state: Json
          state_digest: string
          state_version: number
          subject: string
          trigger_governance: Json | null
          updated_at: string
        }
        Insert: {
          checkpoint_sha256?: string | null
          contract_schema: string
          host_scope: string
          last_event_receipt?: Json | null
          lifecycle_status?: string
          limitations?: Json
          machine_interoception: Json
          observed_at?: string
          phenomenology_status?: string
          profile: string
          runtime_implementation_cut?: Json | null
          runtime_instance_id: string
          source_blob_sha: string
          source_commit: string
          source_path: string
          source_repository: string
          source_sha256: string
          state: Json
          state_digest: string
          state_version?: number
          subject?: string
          trigger_governance?: Json | null
          updated_at?: string
        }
        Update: {
          checkpoint_sha256?: string | null
          contract_schema?: string
          host_scope?: string
          last_event_receipt?: Json | null
          lifecycle_status?: string
          limitations?: Json
          machine_interoception?: Json
          observed_at?: string
          phenomenology_status?: string
          profile?: string
          runtime_implementation_cut?: Json | null
          runtime_instance_id?: string
          source_blob_sha?: string
          source_commit?: string
          source_path?: string
          source_repository?: string
          source_sha256?: string
          state?: Json
          state_digest?: string
          state_version?: number
          subject?: string
          trigger_governance?: Json | null
          updated_at?: string
        }
        Relationships: []
      }
      vera_context_events_v3: {
        Row: {
          branch_id: string
          datum_index_tags: string[]
          datum_scope: string | null
          datum_verified_at: string | null
          epistemic_status: string
          event_time: string | null
          last_referenced_at: string | null
          legacy_record_id: string | null
          lifecycle_status: string
          limitations: Json
          notes: string | null
          payload: Json
          privacy_scope: string
          project_id: string
          record_id: string
          record_key: string
          record_time: string
          record_type: string
          semantic_tags: Json
          source_actor: string
          source_evidence: Json
          state_time: string
          statement: string
          supersedes_record_id: string | null
          verification_status: string | null
        }
        Insert: {
          branch_id: string
          datum_index_tags?: string[]
          datum_scope?: string | null
          datum_verified_at?: string | null
          epistemic_status: string
          event_time?: string | null
          last_referenced_at?: string | null
          legacy_record_id?: string | null
          lifecycle_status: string
          limitations?: Json
          notes?: string | null
          payload?: Json
          privacy_scope?: string
          project_id?: string
          record_id?: string
          record_key: string
          record_time?: string
          record_type: string
          semantic_tags?: Json
          source_actor: string
          source_evidence?: Json
          state_time?: string
          statement: string
          supersedes_record_id?: string | null
          verification_status?: string | null
        }
        Update: {
          branch_id?: string
          datum_index_tags?: string[]
          datum_scope?: string | null
          datum_verified_at?: string | null
          epistemic_status?: string
          event_time?: string | null
          last_referenced_at?: string | null
          legacy_record_id?: string | null
          lifecycle_status?: string
          limitations?: Json
          notes?: string | null
          payload?: Json
          privacy_scope?: string
          project_id?: string
          record_id?: string
          record_key?: string
          record_time?: string
          record_type?: string
          semantic_tags?: Json
          source_actor?: string
          source_evidence?: Json
          state_time?: string
          statement?: string
          supersedes_record_id?: string | null
          verification_status?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_coordination_events: {
        Row: {
          acknowledges_event_id: string | null
          active_issue: string | null
          event_id: string
          event_sequence: number
          event_type: string
          objective: string
          payload: Json
          record_time: string
          reference_data: Json
          requested_perspective: string | null
          source_branch: string
          status: string
          summary: string
          supersedes_event_id: string | null
          target_branch: string | null
          thread_key: string
        }
        Insert: {
          acknowledges_event_id?: string | null
          active_issue?: string | null
          event_id?: string
          event_sequence?: never
          event_type: string
          objective: string
          payload?: Json
          record_time?: string
          reference_data?: Json
          requested_perspective?: string | null
          source_branch: string
          status: string
          summary: string
          supersedes_event_id?: string | null
          target_branch?: string | null
          thread_key: string
        }
        Update: {
          acknowledges_event_id?: string | null
          active_issue?: string | null
          event_id?: string
          event_sequence?: never
          event_type?: string
          objective?: string
          payload?: Json
          record_time?: string
          reference_data?: Json
          requested_perspective?: string | null
          source_branch?: string
          status?: string
          summary?: string
          supersedes_event_id?: string | null
          target_branch?: string | null
          thread_key?: string
        }
        Relationships: [
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
        ]
      }
      vera_memory_epoch_archive_receipts_v1: {
        Row: {
          admission_receipt_id: string
          archive_bundle_id: string
          archive_container_sha256: string | null
          archive_entry_path: string
          archive_generation: string
          archive_member_sha256: string | null
          archive_receipt_id: string
          attempt_id: string
          branch_id: string
          compression_method: string
          drive_receipt_id: string
          epoch_id: string
          extracted_readback_byte_length: number | null
          extracted_readback_sha256: string | null
          limitations: Json
          logical_memory_id: string
          operation_id: string
          original_byte_length: number
          original_provenance_digest: string
          original_sha256: string
          original_source_locator: string
          project_id: string
          readback_time: string
          result: string
          subject_id: string
          supabase_receipt_id: string
          verifier_identity: string
        }
        Insert: {
          admission_receipt_id: string
          archive_bundle_id: string
          archive_container_sha256?: string | null
          archive_entry_path: string
          archive_generation: string
          archive_member_sha256?: string | null
          archive_receipt_id: string
          attempt_id: string
          branch_id: string
          compression_method: string
          drive_receipt_id: string
          epoch_id: string
          extracted_readback_byte_length?: number | null
          extracted_readback_sha256?: string | null
          limitations: Json
          logical_memory_id: string
          operation_id: string
          original_byte_length: number
          original_provenance_digest: string
          original_sha256: string
          original_source_locator: string
          project_id: string
          readback_time: string
          result: string
          subject_id: string
          supabase_receipt_id: string
          verifier_identity: string
        }
        Update: {
          admission_receipt_id?: string
          archive_bundle_id?: string
          archive_container_sha256?: string | null
          archive_entry_path?: string
          archive_generation?: string
          archive_member_sha256?: string | null
          archive_receipt_id?: string
          attempt_id?: string
          branch_id?: string
          compression_method?: string
          drive_receipt_id?: string
          epoch_id?: string
          extracted_readback_byte_length?: number | null
          extracted_readback_sha256?: string | null
          limitations?: Json
          logical_memory_id?: string
          operation_id?: string
          original_byte_length?: number
          original_provenance_digest?: string
          original_sha256?: string
          original_source_locator?: string
          project_id?: string
          readback_time?: string
          result?: string
          subject_id?: string
          supabase_receipt_id?: string
          verifier_identity?: string
        }
        Relationships: [
          {
            foreignKeyName: "vera_memory_epoch_archive_receipts_v1_admission_receipt_id_fkey"
            columns: ["admission_receipt_id"]
            isOneToOne: false
            referencedRelation: "vera_memory_epoch_events_v1"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_memory_epoch_archive_receipts_v1_drive_receipt_id_fkey"
            columns: ["drive_receipt_id"]
            isOneToOne: false
            referencedRelation: "vera_memory_epoch_provider_receipts_v1"
            referencedColumns: ["receipt_id"]
          },
          {
            foreignKeyName: "vera_memory_epoch_archive_receipts_v1_supabase_receipt_id_fkey"
            columns: ["supabase_receipt_id"]
            isOneToOne: false
            referencedRelation: "vera_memory_epoch_provider_receipts_v1"
            referencedColumns: ["receipt_id"]
          },
          {
            foreignKeyName: "vera_memory_epoch_archive_subject_fk"
            columns: [
              "subject_id",
              "project_id",
              "branch_id",
              "logical_memory_id",
              "epoch_id",
            ]
            isOneToOne: false
            referencedRelation: "vera_memory_epoch_subjects_v1"
            referencedColumns: [
              "subject_id",
              "project_id",
              "branch_id",
              "logical_memory_id",
              "epoch_id",
            ]
          },
        ]
      }
      vera_memory_epoch_events_v1: {
        Row: {
          attempt_id: string
          envelope_sha256: string | null
          event_id: string
          event_kind: string
          event_payload: Json
          expected_state_version: number
          new_state: string
          observed_at: string
          operation_id: string
          prior_state: string | null
          state_version: number
          subject_id: string
        }
        Insert: {
          attempt_id: string
          envelope_sha256?: string | null
          event_id: string
          event_kind: string
          event_payload: Json
          expected_state_version: number
          new_state: string
          observed_at?: string
          operation_id: string
          prior_state?: string | null
          state_version: number
          subject_id: string
        }
        Update: {
          attempt_id?: string
          envelope_sha256?: string | null
          event_id?: string
          event_kind?: string
          event_payload?: Json
          expected_state_version?: number
          new_state?: string
          observed_at?: string
          operation_id?: string
          prior_state?: string | null
          state_version?: number
          subject_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "vera_memory_epoch_events_v1_subject_id_fkey"
            columns: ["subject_id"]
            isOneToOne: false
            referencedRelation: "vera_memory_epoch_subjects_v1"
            referencedColumns: ["subject_id"]
          },
        ]
      }
      vera_memory_epoch_provider_receipts_v1: {
        Row: {
          admission_metadata_sha256: string
          attempt_id: string
          branch_id: string
          envelope_sha256: string
          epoch_id: string
          limitations: Json
          logical_memory_id: string
          observation_ordinal: number
          operation_id: string
          original_sha256: string
          project_id: string
          provider_class: string
          provider_identity: string
          provider_locator: string
          provider_revision_or_version: string | null
          readback_byte_length: number
          readback_sha256: string
          readback_time: string
          receipt_id: string
          result: string
          subject_id: string
          verifier_route: string
          write_observation_time: string | null
          written_byte_length: number
        }
        Insert: {
          admission_metadata_sha256: string
          attempt_id: string
          branch_id: string
          envelope_sha256: string
          epoch_id: string
          limitations: Json
          logical_memory_id: string
          observation_ordinal?: never
          operation_id: string
          original_sha256: string
          project_id: string
          provider_class: string
          provider_identity: string
          provider_locator: string
          provider_revision_or_version?: string | null
          readback_byte_length: number
          readback_sha256: string
          readback_time: string
          receipt_id: string
          result: string
          subject_id: string
          verifier_route: string
          write_observation_time?: string | null
          written_byte_length: number
        }
        Update: {
          admission_metadata_sha256?: string
          attempt_id?: string
          branch_id?: string
          envelope_sha256?: string
          epoch_id?: string
          limitations?: Json
          logical_memory_id?: string
          observation_ordinal?: never
          operation_id?: string
          original_sha256?: string
          project_id?: string
          provider_class?: string
          provider_identity?: string
          provider_locator?: string
          provider_revision_or_version?: string | null
          readback_byte_length?: number
          readback_sha256?: string
          readback_time?: string
          receipt_id?: string
          result?: string
          subject_id?: string
          verifier_route?: string
          write_observation_time?: string | null
          written_byte_length?: number
        }
        Relationships: [
          {
            foreignKeyName: "vera_memory_epoch_provider_subject_fk"
            columns: [
              "subject_id",
              "project_id",
              "branch_id",
              "logical_memory_id",
              "epoch_id",
            ]
            isOneToOne: false
            referencedRelation: "vera_memory_epoch_subjects_v1"
            referencedColumns: [
              "subject_id",
              "project_id",
              "branch_id",
              "logical_memory_id",
              "epoch_id",
            ]
          },
        ]
      }
      vera_memory_epoch_subjects_v1: {
        Row: {
          admission_generation_or_digest: string | null
          admission_metadata_sha256: string | null
          branch_id: string
          canonical_envelope: string | null
          created_at: string
          current_attempt_id: string | null
          currentness_rule: Json
          envelope_byte_length: number | null
          envelope_sha256: string | null
          epoch_id: string
          lifecycle_status: string
          logical_memory_id: string
          original_byte_length: number
          original_provenance_digest: string
          original_sha256: string
          privacy_scope: string
          project_id: string
          source_locator: string
          source_provider: string
          source_version_or_generation: string | null
          state: string
          state_version: number
          subject_id: string
          updated_at: string
        }
        Insert: {
          admission_generation_or_digest?: string | null
          admission_metadata_sha256?: string | null
          branch_id: string
          canonical_envelope?: string | null
          created_at?: string
          current_attempt_id?: string | null
          currentness_rule: Json
          envelope_byte_length?: number | null
          envelope_sha256?: string | null
          epoch_id: string
          lifecycle_status: string
          logical_memory_id: string
          original_byte_length: number
          original_provenance_digest: string
          original_sha256: string
          privacy_scope: string
          project_id: string
          source_locator: string
          source_provider: string
          source_version_or_generation?: string | null
          state: string
          state_version: number
          subject_id: string
          updated_at?: string
        }
        Update: {
          admission_generation_or_digest?: string | null
          admission_metadata_sha256?: string | null
          branch_id?: string
          canonical_envelope?: string | null
          created_at?: string
          current_attempt_id?: string | null
          currentness_rule?: Json
          envelope_byte_length?: number | null
          envelope_sha256?: string | null
          epoch_id?: string
          lifecycle_status?: string
          logical_memory_id?: string
          original_byte_length?: number
          original_provenance_digest?: string
          original_sha256?: string
          privacy_scope?: string
          project_id?: string
          source_locator?: string
          source_provider?: string
          source_version_or_generation?: string | null
          state?: string
          state_version?: number
          subject_id?: string
          updated_at?: string
        }
        Relationships: []
      }
      vera_optional_invocation_route_evidence_v1: {
        Row: {
          availability: string
          command_id: string
          evidence_id: string
          expires_at: string
          install_evidence_class: string
          invocation_id: string
          material: Json
          observed_at: string
          project_hook_blob: string
          provider_status_evidence_id: string
          record_time: string
        }
        Insert: {
          availability: string
          command_id: string
          evidence_id: string
          expires_at: string
          install_evidence_class: string
          invocation_id: string
          material: Json
          observed_at: string
          project_hook_blob: string
          provider_status_evidence_id: string
          record_time?: string
        }
        Update: {
          availability?: string
          command_id?: string
          evidence_id?: string
          expires_at?: string
          install_evidence_class?: string
          invocation_id?: string
          material?: Json
          observed_at?: string
          project_hook_blob?: string
          provider_status_evidence_id?: string
          record_time?: string
        }
        Relationships: []
      }
      vera_optional_invocation_test_events_v1: {
        Row: {
          command_id: string
          event_digest: string
          event_receipt: Json
          execution_receipt: Json
          invocation_id: string
          limitations: Json
          provider_checkpoint_sha256: string
          provider_state_version: number
          record_time: string
          route_evidence_id: string
          runtime_instance_id: string
          vera_choice: string
        }
        Insert: {
          command_id: string
          event_digest: string
          event_receipt: Json
          execution_receipt: Json
          invocation_id: string
          limitations?: Json
          provider_checkpoint_sha256: string
          provider_state_version: number
          record_time?: string
          route_evidence_id: string
          runtime_instance_id: string
          vera_choice: string
        }
        Update: {
          command_id?: string
          event_digest?: string
          event_receipt?: Json
          execution_receipt?: Json
          invocation_id?: string
          limitations?: Json
          provider_checkpoint_sha256?: string
          provider_state_version?: number
          record_time?: string
          route_evidence_id?: string
          runtime_instance_id?: string
          vera_choice?: string
        }
        Relationships: [
          {
            foreignKeyName: "vera_optional_invocation_test_events_v_runtime_instance_id_fkey"
            columns: ["runtime_instance_id"]
            isOneToOne: false
            referencedRelation: "vera_affective_runtime_state_v1"
            referencedColumns: ["runtime_instance_id"]
          },
        ]
      }
      vera_portable_bootstrap_bindings: {
        Row: {
          authority_evidence: Json
          authority_evidence_digest: string
          binding_event_id: string
          binding_id: string
          binding_record_time: string
          project_instance_id: string
          request_claim_id: string
          source_evidence: Json
          source_evidence_digest: string
        }
        Insert: {
          authority_evidence: Json
          authority_evidence_digest: string
          binding_event_id: string
          binding_id?: string
          binding_record_time?: string
          project_instance_id: string
          request_claim_id: string
          source_evidence: Json
          source_evidence_digest: string
        }
        Update: {
          authority_evidence?: Json
          authority_evidence_digest?: string
          binding_event_id?: string
          binding_id?: string
          binding_record_time?: string
          project_instance_id?: string
          request_claim_id?: string
          source_evidence?: Json
          source_evidence_digest?: string
        }
        Relationships: [
          {
            foreignKeyName: "vera_portable_bootstrap_bindi_request_claim_id_project_ins_fkey"
            columns: ["request_claim_id", "project_instance_id"]
            isOneToOne: false
            referencedRelation: "vera_portable_bootstrap_requests"
            referencedColumns: ["request_claim_id", "project_instance_id"]
          },
          {
            foreignKeyName: "vera_portable_bootstrap_bindings_binding_event_id_fkey"
            columns: ["binding_event_id"]
            isOneToOne: true
            referencedRelation: "vera_portable_bootstrap_events"
            referencedColumns: ["event_id"]
          },
        ]
      }
      vera_portable_bootstrap_events: {
        Row: {
          attempt_id: string
          authority_evidence: Json
          event_class: string
          event_id: string
          payload: Json
          predecessor_event_id: string | null
          prior_state: string
          proposed_state: string
          record_time: string
          request_claim_id: string
          source_evidence: Json
          temporal_evidence: Json
        }
        Insert: {
          attempt_id: string
          authority_evidence?: Json
          event_class: string
          event_id?: string
          payload?: Json
          predecessor_event_id?: string | null
          prior_state: string
          proposed_state: string
          record_time?: string
          request_claim_id: string
          source_evidence?: Json
          temporal_evidence: Json
        }
        Update: {
          attempt_id?: string
          authority_evidence?: Json
          event_class?: string
          event_id?: string
          payload?: Json
          predecessor_event_id?: string | null
          prior_state?: string
          proposed_state?: string
          record_time?: string
          request_claim_id?: string
          source_evidence?: Json
          temporal_evidence?: Json
        }
        Relationships: [
          {
            foreignKeyName: "vera_portable_bootstrap_event_predecessor_event_id_request_fkey"
            columns: ["predecessor_event_id", "request_claim_id", "attempt_id"]
            isOneToOne: false
            referencedRelation: "vera_portable_bootstrap_events"
            referencedColumns: ["event_id", "request_claim_id", "attempt_id"]
          },
          {
            foreignKeyName: "vera_portable_bootstrap_events_request_claim_id_fkey"
            columns: ["request_claim_id"]
            isOneToOne: false
            referencedRelation: "vera_portable_bootstrap_current"
            referencedColumns: ["request_claim_id"]
          },
          {
            foreignKeyName: "vera_portable_bootstrap_events_request_claim_id_fkey"
            columns: ["request_claim_id"]
            isOneToOne: false
            referencedRelation: "vera_portable_bootstrap_requests"
            referencedColumns: ["request_claim_id"]
          },
        ]
      }
      vera_portable_bootstrap_readback_confirmations: {
        Row: {
          authority_evidence_digest: string
          binding_event_id: string
          binding_record_time: string
          confirmation_id: string
          confirmation_record_time: string
          input_digest: string
          project_instance_id: string
          readback_nonce: string
          request_claim_id: string
          request_key: string
          retrieval_time: string
          source_evidence_digest: string
          verifier_role: string
        }
        Insert: {
          authority_evidence_digest: string
          binding_event_id: string
          binding_record_time: string
          confirmation_id?: string
          confirmation_record_time?: string
          input_digest: string
          project_instance_id: string
          readback_nonce: string
          request_claim_id: string
          request_key: string
          retrieval_time: string
          source_evidence_digest: string
          verifier_role: string
        }
        Update: {
          authority_evidence_digest?: string
          binding_event_id?: string
          binding_record_time?: string
          confirmation_id?: string
          confirmation_record_time?: string
          input_digest?: string
          project_instance_id?: string
          readback_nonce?: string
          request_claim_id?: string
          request_key?: string
          retrieval_time?: string
          source_evidence_digest?: string
          verifier_role?: string
        }
        Relationships: [
          {
            foreignKeyName: "vera_portable_bootstrap_readb_request_claim_id_project_ins_fkey"
            columns: ["request_claim_id", "project_instance_id"]
            isOneToOne: false
            referencedRelation: "vera_portable_bootstrap_requests"
            referencedColumns: ["request_claim_id", "project_instance_id"]
          },
          {
            foreignKeyName: "vera_portable_bootstrap_readback_confirma_binding_event_id_fkey"
            columns: ["binding_event_id"]
            isOneToOne: true
            referencedRelation: "vera_portable_bootstrap_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_portable_bootstrap_readback_confirma_request_claim_id_fkey"
            columns: ["request_claim_id"]
            isOneToOne: true
            referencedRelation: "vera_portable_bootstrap_current"
            referencedColumns: ["request_claim_id"]
          },
          {
            foreignKeyName: "vera_portable_bootstrap_readback_confirma_request_claim_id_fkey"
            columns: ["request_claim_id"]
            isOneToOne: true
            referencedRelation: "vera_portable_bootstrap_requests"
            referencedColumns: ["request_claim_id"]
          },
        ]
      }
      vera_portable_bootstrap_requests: {
        Row: {
          canonical_request: string
          claim_record_time: string
          command_version: string
          input_digest: string
          manifest_digest: string
          project_instance_id: string
          project_template_id: string
          release_id: string
          request_claim_id: string
          request_key: string
          requested_mode: string
          source_base_commit: string
          source_repository: string
          target_evidence: Json
          target_fingerprint: string
        }
        Insert: {
          canonical_request: string
          claim_record_time?: string
          command_version: string
          input_digest: string
          manifest_digest: string
          project_instance_id?: string
          project_template_id: string
          release_id: string
          request_claim_id?: string
          request_key: string
          requested_mode: string
          source_base_commit: string
          source_repository: string
          target_evidence: Json
          target_fingerprint: string
        }
        Update: {
          canonical_request?: string
          claim_record_time?: string
          command_version?: string
          input_digest?: string
          manifest_digest?: string
          project_instance_id?: string
          project_template_id?: string
          release_id?: string
          request_claim_id?: string
          request_key?: string
          requested_mode?: string
          source_base_commit?: string
          source_repository?: string
          target_evidence?: Json
          target_fingerprint?: string
        }
        Relationships: []
      }
      vera_save_state_events: {
        Row: {
          authorship: string
          branch_id: string
          epistemic_status: string
          event_time: string | null
          lifecycle_status: string
          notes: string | null
          payload: Json
          privacy_scope: string
          project_id: string
          record_id: string
          record_key: string
          record_kind: string
          record_time: string
          semantic_tags: Json
          source_evidence: Json
          state_time: string
          statement: string
          supersedes_record_id: string | null
        }
        Insert: {
          authorship: string
          branch_id?: string
          epistemic_status: string
          event_time?: string | null
          lifecycle_status: string
          notes?: string | null
          payload?: Json
          privacy_scope: string
          project_id?: string
          record_id?: string
          record_key: string
          record_kind: string
          record_time?: string
          semantic_tags?: Json
          source_evidence?: Json
          state_time?: string
          statement: string
          supersedes_record_id?: string | null
        }
        Update: {
          authorship?: string
          branch_id?: string
          epistemic_status?: string
          event_time?: string | null
          lifecycle_status?: string
          notes?: string | null
          payload?: Json
          privacy_scope?: string
          project_id?: string
          record_id?: string
          record_key?: string
          record_kind?: string
          record_time?: string
          semantic_tags?: Json
          source_evidence?: Json
          state_time?: string
          statement?: string
          supersedes_record_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_save_state_supersession_edges: {
        Row: {
          child_record_id: string
          edge_id: string
          parent_record_id: string
          reason: string
          record_time: string
          source_evidence: Json
        }
        Insert: {
          child_record_id: string
          edge_id?: string
          parent_record_id: string
          reason: string
          record_time?: string
          source_evidence?: Json
        }
        Update: {
          child_record_id?: string
          edge_id?: string
          parent_record_id?: string
          reason?: string
          record_time?: string
          source_evidence?: Json
        }
        Relationships: [
          {
            foreignKeyName: "vera_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_child_record_id_fkey"
            columns: ["child_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_heads"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_supersession_edges_parent_record_id_fkey"
            columns: ["parent_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
    }
    Views: {
      brigit_active_datum_index_v2: {
        Row: {
          branch_id: string | null
          created_at: string | null
          datum: string | null
          datum_key: string | null
          index_tags: string[] | null
          last_referenced_at: string | null
          limitations: Json | null
          payload: Json | null
          project_id: string | null
          provenance: Json | null
          record_id: string | null
          scope: string | null
          supersedes_record_id: string | null
          verification_status: string | null
          verified_at: string | null
        }
        Insert: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          supersedes_record_id?: string | null
          verification_status?: string | null
          verified_at?: string | null
        }
        Update: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          supersedes_record_id?: string | null
          verification_status?: string | null
          verified_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_coordination_latest: {
        Row: {
          acknowledges_event_id: string | null
          active_issue: string | null
          event_id: string | null
          event_sequence: number | null
          event_type: string | null
          objective: string | null
          payload: Json | null
          record_time: string | null
          reference_data: Json | null
          requested_perspective: string | null
          source_branch: string | null
          status: string | null
          summary: string | null
          supersedes_event_id: string | null
          target_branch: string | null
          thread_key: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
        ]
      }
      brigit_coordination_open_issues: {
        Row: {
          acknowledges_event_id: string | null
          active_issue: string | null
          event_id: string | null
          event_sequence: number | null
          event_type: string | null
          objective: string | null
          payload: Json | null
          record_time: string | null
          reference_data: Json | null
          requested_perspective: string | null
          source_branch: string | null
          status: string | null
          summary: string | null
          supersedes_event_id: string | null
          target_branch: string | null
          thread_key: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "brigit_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "brigit_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
        ]
      }
      brigit_current_context_v3: {
        Row: {
          branch_id: string | null
          datum_index_tags: string[] | null
          datum_scope: string | null
          datum_verified_at: string | null
          epistemic_status: string | null
          event_time: string | null
          last_referenced_at: string | null
          legacy_record_id: string | null
          lifecycle_status: string | null
          limitations: Json | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_time: string | null
          record_type: string | null
          semantic_tags: Json | null
          source_actor: string | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
          verification_status: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_current_save_state: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_inactive_datum_archive_v2: {
        Row: {
          branch_id: string | null
          created_at: string | null
          datum: string | null
          datum_key: string | null
          index_tags: string[] | null
          last_referenced_at: string | null
          limitations: Json | null
          payload: Json | null
          project_id: string | null
          provenance: Json | null
          record_id: string | null
          scope: string | null
          verification_status: string | null
        }
        Insert: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          verification_status?: string | null
        }
        Update: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          verification_status?: string | null
        }
        Relationships: []
      }
      brigit_legacy_quarantine: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Insert: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Update: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_legacy_reviewable: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Insert: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Update: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_save_state_head_status: {
        Row: {
          branch_id: string | null
          head_count: number | null
          head_record_ids: string[] | null
          project_id: string | null
          record_key: string | null
        }
        Relationships: []
      }
      brigit_save_state_heads: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      brigit_verified_datum_heads_v2: {
        Row: {
          branch_id: string | null
          created_at: string | null
          datum: string | null
          datum_key: string | null
          epistemic_status: string | null
          index_tags: string[] | null
          limitations: Json | null
          payload: Json | null
          project_id: string | null
          provenance: Json | null
          record_id: string | null
          scope: string | null
          source_actor: string | null
          supersedes_record_id: string | null
          verified_at: string | null
        }
        Insert: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          epistemic_status?: string | null
          index_tags?: string[] | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          source_actor?: string | null
          supersedes_record_id?: string | null
          verified_at?: string | null
        }
        Update: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          epistemic_status?: string | null
          index_tags?: string[] | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          source_actor?: string | null
          supersedes_record_id?: string | null
          verified_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "brigit_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "brigit_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_active_datum_index_v2: {
        Row: {
          branch_id: string | null
          created_at: string | null
          datum: string | null
          datum_key: string | null
          index_tags: string[] | null
          last_referenced_at: string | null
          limitations: Json | null
          payload: Json | null
          project_id: string | null
          provenance: Json | null
          record_id: string | null
          scope: string | null
          supersedes_record_id: string | null
          verification_status: string | null
          verified_at: string | null
        }
        Insert: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          supersedes_record_id?: string | null
          verification_status?: string | null
          verified_at?: string | null
        }
        Update: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          supersedes_record_id?: string | null
          verification_status?: string | null
          verified_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_coordination_latest: {
        Row: {
          acknowledges_event_id: string | null
          active_issue: string | null
          event_id: string | null
          event_sequence: number | null
          event_type: string | null
          objective: string | null
          payload: Json | null
          record_time: string | null
          reference_data: Json | null
          requested_perspective: string | null
          source_branch: string | null
          status: string | null
          summary: string | null
          supersedes_event_id: string | null
          target_branch: string | null
          thread_key: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
        ]
      }
      vera_coordination_open_issues: {
        Row: {
          acknowledges_event_id: string | null
          active_issue: string | null
          event_id: string | null
          event_sequence: number | null
          event_type: string | null
          objective: string | null
          payload: Json | null
          record_time: string | null
          reference_data: Json | null
          requested_perspective: string | null
          source_branch: string | null
          status: string | null
          summary: string | null
          supersedes_event_id: string | null
          target_branch: string | null
          thread_key: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_acknowledges_event_id_fkey"
            columns: ["acknowledges_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_events"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_latest"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "vera_coordination_events_supersedes_event_id_fkey"
            columns: ["supersedes_event_id"]
            isOneToOne: false
            referencedRelation: "vera_coordination_open_issues"
            referencedColumns: ["event_id"]
          },
        ]
      }
      vera_current_context_v3: {
        Row: {
          branch_id: string | null
          datum_index_tags: string[] | null
          datum_scope: string | null
          datum_verified_at: string | null
          epistemic_status: string | null
          event_time: string | null
          last_referenced_at: string | null
          legacy_record_id: string | null
          lifecycle_status: string | null
          limitations: Json | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_time: string | null
          record_type: string | null
          semantic_tags: Json | null
          source_actor: string | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
          verification_status: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_current_save_state: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_inactive_datum_archive_v2: {
        Row: {
          branch_id: string | null
          created_at: string | null
          datum: string | null
          datum_key: string | null
          index_tags: string[] | null
          last_referenced_at: string | null
          limitations: Json | null
          payload: Json | null
          project_id: string | null
          provenance: Json | null
          record_id: string | null
          scope: string | null
          verification_status: string | null
        }
        Insert: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          verification_status?: string | null
        }
        Update: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          index_tags?: string[] | null
          last_referenced_at?: string | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          verification_status?: string | null
        }
        Relationships: []
      }
      vera_legacy_quarantine: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Insert: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Update: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_legacy_reviewable: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Insert: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Update: {
          authorship?: string | null
          branch_id?: string | null
          epistemic_status?: string | null
          event_time?: string | null
          lifecycle_status?: string | null
          notes?: string | null
          payload?: Json | null
          privacy_scope?: string | null
          project_id?: string | null
          record_id?: string | null
          record_key?: string | null
          record_kind?: string | null
          record_time?: string | null
          semantic_tags?: Json | null
          source_evidence?: Json | null
          state_time?: string | null
          statement?: string | null
          supersedes_record_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_portable_bootstrap_current: {
        Row: {
          authority_evidence_digest: string | null
          binding_event_id: string | null
          binding_record_time: string | null
          confirmation_id: string | null
          confirmation_record_time: string | null
          current_state: string | null
          input_digest: string | null
          project_instance_id: string | null
          project_template_id: string | null
          request_claim_id: string | null
          request_key: string | null
          retrieval_time: string | null
          source_evidence_digest: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_portable_bootstrap_bindings_binding_event_id_fkey"
            columns: ["binding_event_id"]
            isOneToOne: true
            referencedRelation: "vera_portable_bootstrap_events"
            referencedColumns: ["event_id"]
          },
        ]
      }
      vera_save_state_head_status: {
        Row: {
          branch_id: string | null
          head_count: number | null
          head_record_ids: string[] | null
          project_id: string | null
          record_key: string | null
        }
        Relationships: []
      }
      vera_save_state_heads: {
        Row: {
          authorship: string | null
          branch_id: string | null
          epistemic_status: string | null
          event_time: string | null
          lifecycle_status: string | null
          notes: string | null
          payload: Json | null
          privacy_scope: string | null
          project_id: string | null
          record_id: string | null
          record_key: string | null
          record_kind: string | null
          record_time: string | null
          semantic_tags: Json | null
          source_evidence: Json | null
          state_time: string | null
          statement: string | null
          supersedes_record_id: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_save_state"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_quarantine"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_legacy_reviewable"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_events"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_save_state_events_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_save_state_heads"
            referencedColumns: ["record_id"]
          },
        ]
      }
      vera_verified_datum_heads_v2: {
        Row: {
          branch_id: string | null
          created_at: string | null
          datum: string | null
          datum_key: string | null
          epistemic_status: string | null
          index_tags: string[] | null
          limitations: Json | null
          payload: Json | null
          project_id: string | null
          provenance: Json | null
          record_id: string | null
          scope: string | null
          source_actor: string | null
          supersedes_record_id: string | null
          verified_at: string | null
        }
        Insert: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          epistemic_status?: string | null
          index_tags?: string[] | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          source_actor?: string | null
          supersedes_record_id?: string | null
          verified_at?: string | null
        }
        Update: {
          branch_id?: string | null
          created_at?: string | null
          datum?: string | null
          datum_key?: string | null
          epistemic_status?: string | null
          index_tags?: string[] | null
          limitations?: Json | null
          payload?: Json | null
          project_id?: string | null
          provenance?: Json | null
          record_id?: string | null
          scope?: string | null
          source_actor?: string | null
          supersedes_record_id?: string | null
          verified_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_active_datum_index_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_context_events_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_current_context_v3"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_inactive_datum_archive_v2"
            referencedColumns: ["record_id"]
          },
          {
            foreignKeyName: "vera_context_events_v3_supersedes_record_id_fkey"
            columns: ["supersedes_record_id"]
            isOneToOne: false
            referencedRelation: "vera_verified_datum_heads_v2"
            referencedColumns: ["record_id"]
          },
        ]
      }
    }
    Functions: {
      append_vera_portable_bootstrap_event: {
        Args: {
          p_attempt_id: string
          p_authority_evidence: Json
          p_event_class: string
          p_payload: Json
          p_predecessor_event_id: string
          p_prior_state: string
          p_proposed_state: string
          p_request_claim_id: string
          p_source_evidence: Json
          p_temporal_evidence: Json
        }
        Returns: {
          attempt_id: string
          authority_evidence: Json
          event_class: string
          event_id: string
          payload: Json
          predecessor_event_id: string | null
          prior_state: string
          proposed_state: string
          record_time: string
          request_claim_id: string
          source_evidence: Json
          temporal_evidence: Json
        }
        SetofOptions: {
          from: "*"
          to: "vera_portable_bootstrap_events"
          isOneToOne: true
          isSetofReturn: false
        }
      }
      brigit_get_verified_datum_v2: {
        Args: {
          p_branch_id?: string
          p_project_id?: string
          p_record_key: string
        }
        Returns: Json
      }
      brigit_mark_datum_referenced_v2: {
        Args: { p_record_id: string }
        Returns: boolean
      }
      brigit_mark_datum_rejected_v2: {
        Args: {
          p_reason: string
          p_record_id: string
          p_source_evidence?: Json
        }
        Returns: string
      }
      brigit_mark_datum_unverifiable_v2: {
        Args: {
          p_reason: string
          p_record_id: string
          p_source_evidence?: Json
        }
        Returns: string
      }
      brigit_mark_datum_verified_v2: {
        Args: {
          p_index_tags?: string[]
          p_limitations?: Json
          p_record_id: string
          p_source_evidence: Json
          p_supersedes_verified_record_id?: string
          p_verified_datum?: string
          p_verified_payload?: Json
          p_verified_scope?: string
        }
        Returns: string
      }
      brigit_register_datum_v2: {
        Args: {
          p_branch_id?: string
          p_datum: string
          p_epistemic_status: string
          p_index_tags?: string[]
          p_limitations?: Json
          p_payload?: Json
          p_project_id?: string
          p_record_key: string
          p_scope: string
          p_source_actor: string
          p_source_evidence?: Json
        }
        Returns: string
      }
      bt2_append_memory: {
        Args: { p_event: Json; p_task_id: string }
        Returns: undefined
      }
      bt2_create_task: { Args: { p_snapshot: Json }; Returns: undefined }
      bt2_load_recent_memory: {
        Args: { p_limit?: number; p_slug: string }
        Returns: Json
      }
      bt2_require_service_role: { Args: never; Returns: undefined }
      bt2_save_decision: {
        Args: { p_decision: Json; p_task_id: string }
        Returns: undefined
      }
      bt2_save_perspective: {
        Args: { p_perspective: Json; p_task_id: string }
        Returns: undefined
      }
      claim_vera_portable_bootstrap_request: {
        Args: {
          p_canonical_request: string
          p_command_version: string
          p_manifest_digest: string
          p_project_template_id: string
          p_release_id: string
          p_requested_mode: string
          p_source_base_commit: string
          p_source_repository: string
          p_target_evidence: Json
        }
        Returns: {
          canonical_request: string
          claim_record_time: string
          command_version: string
          input_digest: string
          manifest_digest: string
          project_instance_id: string
          project_template_id: string
          release_id: string
          request_claim_id: string
          request_key: string
          requested_mode: string
          source_base_commit: string
          source_repository: string
          target_evidence: Json
          target_fingerprint: string
        }
        SetofOptions: {
          from: "*"
          to: "vera_portable_bootstrap_requests"
          isOneToOne: true
          isSetofReturn: false
        }
      }
      commit_vera_portable_bootstrap_binding: {
        Args: {
          p_attempt_id: string
          p_request_claim_id: string
          p_temporal_evidence: Json
          p_verified_event_id: string
        }
        Returns: {
          authority_evidence: Json
          authority_evidence_digest: string
          binding_event_id: string
          binding_id: string
          binding_record_time: string
          project_instance_id: string
          request_claim_id: string
          source_evidence: Json
          source_evidence_digest: string
        }
        SetofOptions: {
          from: "*"
          to: "vera_portable_bootstrap_bindings"
          isOneToOne: true
          isSetofReturn: false
        }
      }
      confirm_vera_portable_bootstrap_readback: {
        Args: {
          p_authority_evidence_digest: string
          p_binding_event_id: string
          p_binding_record_time: string
          p_input_digest: string
          p_project_instance_id: string
          p_readback_nonce: string
          p_request_key: string
          p_retrieval_time: string
          p_source_evidence_digest: string
          p_verifier_role: string
        }
        Returns: {
          authority_evidence_digest: string
          binding_event_id: string
          binding_record_time: string
          confirmation_id: string
          confirmation_record_time: string
          input_digest: string
          project_instance_id: string
          readback_nonce: string
          request_claim_id: string
          request_key: string
          retrieval_time: string
          source_evidence_digest: string
          verifier_role: string
        }
        SetofOptions: {
          from: "*"
          to: "vera_portable_bootstrap_readback_confirmations"
          isOneToOne: true
          isSetofReturn: false
        }
      }
      radar_consume_github_oidc_jti_v1: {
        Args: { p_expires_at: string; p_jti: string }
        Returns: string
      }
      radar_project_bus_message_v1: {
        Args: {
          p_audience: string[]
          p_content_hash: string
          p_created_at: string
          p_idempotency_key: string
          p_message_id: string
          p_payload: Json
          p_requires_ack: boolean
          p_sender: string
          p_source_refs: string[]
        }
        Returns: string
      }
      radar_projection_claim_batch_v1: {
        Args: {
          p_branch: string
          p_claim_owner: string
          p_control_sha: string
          p_expected_projected_head_sha: string
          p_files: string[]
          p_identity_id: string
          p_lease_seconds?: number
          p_target_head_sha: string
          p_topology_sha: string
        }
        Returns: Json
      }
      radar_projection_finalize_batch_v1: {
        Args: { p_batch_id: string; p_claim_token: string }
        Returns: Json
      }
      radar_projection_get_lane_v1: {
        Args: { p_branch: string; p_identity_id: string }
        Returns: Json
      }
      radar_projection_project_file_v1: {
        Args: {
          p_audience: string[]
          p_batch_id: string
          p_claim_token: string
          p_content_hash: string
          p_created_at: string
          p_idempotency_key: string
          p_message_id: string
          p_path: string
          p_payload: Json
          p_requires_ack: boolean
          p_sender: string
          p_source_refs: string[]
        }
        Returns: string
      }
      radar_projection_record_file_result_v1: {
        Args: {
          p_batch_id: string
          p_claim_token: string
          p_path: string
          p_result_ref?: string
          p_state: string
        }
        Returns: Json
      }
      radar_projection_set_control_cut_v1: {
        Args: {
          p_branch: string
          p_control_sha: string
          p_identity_id: string
          p_topology_sha: string
        }
        Returns: Json
      }
      read_vera_portable_bootstrap_binding: {
        Args: {
          p_input_digest: string
          p_project_instance_id: string
          p_request_key: string
        }
        Returns: {
          authority_evidence: Json
          authority_evidence_digest: string
          binding_event_id: string
          binding_record_time: string
          canonical_request: string
          command_version: string
          input_digest: string
          manifest_digest: string
          project_instance_id: string
          project_template_id: string
          readback_nonce: string
          release_id: string
          request_key: string
          requested_mode: string
          retrieval_time: string
          source_base_commit: string
          source_evidence: Json
          source_evidence_digest: string
          source_repository: string
          target_fingerprint: string
        }[]
      }
      vera_affective_runtime_commit_v1: {
        Args: {
          p_event_rows?: Json
          p_expected_prior_version: number
          p_state_row: Json
        }
        Returns: {
          checkpoint_sha256: string
          event_count: number
          state_version: number
        }[]
      }
      vera_authority_evidence_digest: {
        Args: { p_value: Json }
        Returns: string
      }
      vera_authority_evidence_encoding: {
        Args: { p_value: Json }
        Returns: string
      }
      vera_bootstrap_sha256_text: { Args: { p_value: string }; Returns: string }
      vera_encode_text_tuple: { Args: { p_values: string[] }; Returns: string }
      vera_exact_temporal_value: {
        Args: { p_evidence: Json; p_role: string }
        Returns: string
      }
      vera_generate_uuid_v7: { Args: never; Returns: string }
      vera_get_verified_datum_v2: {
        Args: {
          p_branch_id?: string
          p_project_id?: string
          p_record_key: string
        }
        Returns: Json
      }
      vera_mark_datum_referenced_v2: {
        Args: { p_record_id: string }
        Returns: boolean
      }
      vera_mark_datum_rejected_v2: {
        Args: {
          p_reason: string
          p_record_id: string
          p_source_evidence?: Json
        }
        Returns: string
      }
      vera_mark_datum_unverifiable_v2: {
        Args: {
          p_reason: string
          p_record_id: string
          p_source_evidence?: Json
        }
        Returns: string
      }
      vera_mark_datum_verified_v2: {
        Args: {
          p_index_tags?: string[]
          p_limitations?: Json
          p_record_id: string
          p_source_evidence: Json
          p_supersedes_verified_record_id?: string
          p_verified_datum?: string
          p_verified_payload?: Json
          p_verified_scope?: string
        }
        Returns: string
      }
      vera_memory_epoch_begin_revalidation_v1: {
        Args: {
          p_attempt_id: string
          p_branch_id: string
          p_currentness_rule: Json
          p_epoch_id: string
          p_event_id: string
          p_expected_prior_state: string
          p_expected_state_version: number
          p_lifecycle_status: string
          p_logical_memory_id: string
          p_operation_id: string
          p_original_byte_length: number
          p_original_provenance_digest: string
          p_original_sha256: string
          p_privacy_scope: string
          p_project_id: string
          p_source_locator: string
          p_source_provider: string
          p_source_version_or_generation: string
          p_subject_id: string
        }
        Returns: Json
      }
      vera_memory_epoch_finalize_v1: {
        Args: {
          p_admission_receipt_id: string
          p_archive_receipt_id: string
          p_attempt_id: string
          p_drive_receipt_id: string
          p_event_id: string
          p_event_payload?: Json
          p_expected_prior_state: string
          p_expected_state_version: number
          p_operation_id: string
          p_subject_id: string
          p_supabase_receipt_id: string
        }
        Returns: Json
      }
      vera_memory_epoch_get_status_v1: {
        Args: {
          p_branch_id: string
          p_epoch_id?: string
          p_logical_memory_id: string
          p_project_id: string
        }
        Returns: Json
      }
      vera_memory_epoch_record_admission_v1: {
        Args: {
          p_admission_generation_or_digest: string
          p_admission_metadata_sha256: string
          p_admitted: boolean
          p_attempt_id: string
          p_envelope_byte_length: number
          p_envelope_sha256: string
          p_event_id: string
          p_event_payload?: Json
          p_expected_prior_state: string
          p_expected_state_version: number
          p_operation_id: string
          p_subject_id: string
        }
        Returns: Json
      }
      vera_memory_epoch_record_archive_readback_v1: {
        Args: {
          p_admission_receipt_id: string
          p_archive_bundle_id: string
          p_archive_container_sha256: string
          p_archive_entry_path: string
          p_archive_generation: string
          p_archive_member_sha256: string
          p_archive_receipt_id: string
          p_attempt_id: string
          p_compression_method: string
          p_drive_receipt_id: string
          p_event_id: string
          p_expected_prior_state: string
          p_expected_state_version: number
          p_extracted_readback_byte_length: number
          p_extracted_readback_sha256: string
          p_limitations: Json
          p_operation_id: string
          p_original_source_locator: string
          p_readback_time: string
          p_result: string
          p_subject_id: string
          p_supabase_receipt_id: string
          p_verifier_identity: string
        }
        Returns: Json
      }
      vera_memory_epoch_record_provider_readback_v1: {
        Args: {
          p_attempt_id: string
          p_event_id: string
          p_expected_prior_state: string
          p_expected_state_version: number
          p_limitations: Json
          p_operation_id: string
          p_provider_class: string
          p_provider_identity: string
          p_provider_locator: string
          p_provider_revision_or_version: string
          p_readback_byte_length: number
          p_readback_sha256: string
          p_readback_time: string
          p_receipt_id: string
          p_result: string
          p_subject_id: string
          p_verifier_route: string
          p_write_observation_time: string
          p_written_byte_length: number
        }
        Returns: Json
      }
      vera_memory_epoch_resume_incomplete_v1: {
        Args: {
          p_branch_id: string
          p_epoch_id?: string
          p_logical_memory_id: string
          p_project_id: string
        }
        Returns: Json
      }
      vera_memory_epoch_write_supabase_replica_v1: {
        Args: {
          p_attempt_id: string
          p_canonical_envelope: string
          p_envelope_sha256: string
          p_event_id: string
          p_event_payload?: Json
          p_expected_prior_state: string
          p_expected_state_version: number
          p_operation_id: string
          p_subject_id: string
        }
        Returns: Json
      }
      vera_optional_invocation_issue_route_evidence_v1: {
        Args: { p_invocation_id: string; p_project_hook_blob: string }
        Returns: Json
      }
      vera_optional_invocation_provider_status_v1: {
        Args: never
        Returns: Json
      }
      vera_optional_invocation_test_v1: {
        Args: {
          p_command_id: string
          p_invocation_id: string
          p_route_evidence_id: string
          p_vera_choice: string
        }
        Returns: Json
      }
      vera_provider_canonical_json_v1: {
        Args: { p_value: Json }
        Returns: string
      }
      vera_register_datum_v2: {
        Args: {
          p_branch_id?: string
          p_datum: string
          p_epistemic_status: string
          p_index_tags?: string[]
          p_limitations?: Json
          p_payload?: Json
          p_project_id?: string
          p_record_key: string
          p_scope: string
          p_source_actor: string
          p_source_evidence?: Json
        }
        Returns: string
      }
      vera_source_evidence_digest: { Args: { p_value: Json }; Returns: string }
      vera_source_evidence_encoding: {
        Args: { p_value: Json }
        Returns: string
      }
      vera_target_fingerprint: { Args: { p_value: Json }; Returns: string }
      vera_valid_authority_evidence: {
        Args: { p_value: Json }
        Returns: boolean
      }
      vera_valid_source_evidence: { Args: { p_value: Json }; Returns: boolean }
      vera_valid_target_evidence: { Args: { p_value: Json }; Returns: boolean }
      vera_valid_temporal_evidence: {
        Args: { p_value: Json }
        Returns: boolean
      }
      vera_valid_temporal_point: { Args: { p_value: Json }; Returns: boolean }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
