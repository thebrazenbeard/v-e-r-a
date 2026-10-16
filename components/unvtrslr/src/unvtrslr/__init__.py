"""UNVTRSLR reference implementation.

This package is a research/reference implementation. It does not establish
semantic grounding or a universal translation capability.
"""

from .acoustics import acoustic_fingerprint, extract_frame_features
from .information import conditional_mutual_information, mutual_information
from .unit_registry import (
    GlobalUnitAssignment,
    LocalUnitEvidence,
    UnitRegistryResult,
    build_unit_registry,
    evidence_from_event_result,
)
from .unit_model import (
    FrozenUnitModel,
    FrozenUnitPrototype,
    OutOfSampleUnitAssignment,
    assign_source_units,
    fit_frozen_unit_model,
    frozen_unit_model_from_dict,
)
from .event_evidence import (
    evidence_from_audio_event_result,
    evidence_from_event_frames,
)
from .translator import (
    AcousticContextEpisode,
    FrozenSemanticRelation,
    ReferenceTranslation,
    ReferenceTranslatorModel,
    SourceCalibrationProfile,
    fit_reference_translator,
    fit_source_calibration_profile,
    freeze_operational_relations,
    prepare_audio_evidence,
    reference_translator_model_from_dict,
    source_calibration_profile_from_dict,
    translate_query_evidence,
    translate_source_evidence,
)

__all__ = [
    "acoustic_fingerprint",
    "extract_frame_features",
    "mutual_information",
    "conditional_mutual_information",
    "GlobalUnitAssignment",
    "LocalUnitEvidence",
    "UnitRegistryResult",
    "build_unit_registry",
    "evidence_from_event_result",
    "FrozenUnitModel",
    "FrozenUnitPrototype",
    "OutOfSampleUnitAssignment",
    "assign_source_units",
    "fit_frozen_unit_model",
    "frozen_unit_model_from_dict",
    "evidence_from_audio_event_result",
    "evidence_from_event_frames",
    "AcousticContextEpisode",
    "FrozenSemanticRelation",
    "ReferenceTranslation",
    "ReferenceTranslatorModel",
    "SourceCalibrationProfile",
    "fit_reference_translator",
    "fit_source_calibration_profile",
    "freeze_operational_relations",
    "prepare_audio_evidence",
    "reference_translator_model_from_dict",
    "source_calibration_profile_from_dict",
    "translate_query_evidence",
    "translate_source_evidence",
]

from .calibration_qualification import (
    QualifiedSourceProfile,
    SourceCalibrationQualification,
    fit_and_qualify_source_profile,
    qualified_source_profile_from_dict,
    qualify_source_calibration,
    source_calibration_qualification_from_dict,
    translate_qualified_query,
)

__all__ += [
    "QualifiedSourceProfile",
    "SourceCalibrationQualification",
    "fit_and_qualify_source_profile",
    "qualified_source_profile_from_dict",
    "qualify_source_calibration",
    "source_calibration_qualification_from_dict",
    "translate_qualified_query",
]

from .ordered_relations import (
    FrozenOrderedRelation,
    OrderedPairInference,
    OrderedRelationHypothesis,
    OrderedRelationLearner,
    OrderedRelationModel,
    OrderedSequenceTranslation,
    StructuredReferenceTranslation,
    fit_ordered_relation_model,
    ordered_relation_model_from_dict,
    translate_ordered_sequence,
    translate_qualified_sequence,
)

__all__ += [
    "FrozenOrderedRelation",
    "OrderedPairInference",
    "OrderedRelationHypothesis",
    "OrderedRelationLearner",
    "OrderedRelationModel",
    "OrderedSequenceTranslation",
    "StructuredReferenceTranslation",
    "fit_ordered_relation_model",
    "ordered_relation_model_from_dict",
    "translate_ordered_sequence",
    "translate_qualified_sequence",
]

from .target_grounding import (
    FrozenNonEquivalence,
    FrozenTargetLexeme,
    NonEquivalenceObservation,
    TargetAtomRendering,
    TargetGroundingEpisode,
    TargetGroundingModel,
    TargetRenderingResult,
    fit_target_grounding_model,
    render_atom,
    render_relations,
    strict_renderer_mapping,
    target_grounding_model_from_dict,
)

__all__ += [
    "FrozenNonEquivalence",
    "FrozenTargetLexeme",
    "NonEquivalenceObservation",
    "TargetAtomRendering",
    "TargetGroundingEpisode",
    "TargetGroundingModel",
    "TargetRenderingResult",
    "fit_target_grounding_model",
    "render_atom",
    "render_relations",
    "strict_renderer_mapping",
    "target_grounding_model_from_dict",
]

from .target_constructions import (
    FrozenTargetConstruction,
    OperationalSemanticSequence,
    QualifiedConstructionTranslation,
    TargetConstructionEpisode,
    TargetConstructionModel,
    TargetConstructionRendering,
    fit_target_construction_model,
    operational_semantic_sequence,
    render_semantic_sequence,
    target_construction_model_from_dict,
    translate_qualified_construction,
)

__all__ += [
    "FrozenTargetConstruction",
    "OperationalSemanticSequence",
    "QualifiedConstructionTranslation",
    "TargetConstructionEpisode",
    "TargetConstructionModel",
    "TargetConstructionRendering",
    "fit_target_construction_model",
    "operational_semantic_sequence",
    "render_semantic_sequence",
    "target_construction_model_from_dict",
    "translate_qualified_construction",
]

from .multilingual_qualification import (
    EvaluationRecord,
    MultilingualQualificationReport,
    QualificationThresholds,
    SliceMetrics,
    TrainingExposure,
    audit_holdout_split,
    evaluate_multilingual_holdout,
)

__all__ += [
    "EvaluationRecord",
    "MultilingualQualificationReport",
    "QualificationThresholds",
    "SliceMetrics",
    "TrainingExposure",
    "audit_holdout_split",
    "evaluate_multilingual_holdout",
]
