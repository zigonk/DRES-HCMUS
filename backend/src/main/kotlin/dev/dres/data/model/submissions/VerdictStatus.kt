package dev.dres.data.model.submissions

import dev.dres.api.rest.types.evaluation.submission.ApiVerdictStatus

enum class VerdictStatus {
        CORRECT, WRONG, INDETERMINATE, UNDECIDABLE, PARTIALLY_CORRECT;

    fun toApi(): ApiVerdictStatus = when(this) {
        CORRECT -> ApiVerdictStatus.CORRECT
        WRONG -> ApiVerdictStatus.WRONG
        INDETERMINATE -> ApiVerdictStatus.INDETERMINATE
        UNDECIDABLE -> ApiVerdictStatus.UNDECIDABLE
        PARTIALLY_CORRECT -> ApiVerdictStatus.PARTIALLY_CORRECT
    }

    fun toDb(): DbVerdictStatus = when(this) {
        CORRECT -> DbVerdictStatus.CORRECT
        WRONG -> DbVerdictStatus.WRONG
        INDETERMINATE -> DbVerdictStatus.INDETERMINATE
        UNDECIDABLE -> DbVerdictStatus.UNDECIDABLE
        PARTIALLY_CORRECT -> DbVerdictStatus.PARTIALLY_CORRECT
    }

    companion object {

        fun fromApi(status: ApiVerdictStatus): VerdictStatus = when(status) {
            ApiVerdictStatus.CORRECT -> CORRECT
            ApiVerdictStatus.WRONG -> WRONG
            ApiVerdictStatus.INDETERMINATE -> INDETERMINATE
            ApiVerdictStatus.UNDECIDABLE -> UNDECIDABLE
            ApiVerdictStatus.PARTIALLY_CORRECT -> PARTIALLY_CORRECT
        }

        fun fromDb(status: DbVerdictStatus): VerdictStatus = when(status) {
            DbVerdictStatus.CORRECT -> CORRECT
            DbVerdictStatus.WRONG -> WRONG
            DbVerdictStatus.INDETERMINATE -> INDETERMINATE
            DbVerdictStatus.UNDECIDABLE -> UNDECIDABLE
            DbVerdictStatus.PARTIALLY_CORRECT -> PARTIALLY_CORRECT
            else -> throw IllegalStateException("Unknown DbVerdictStatus $status")
        }

    }

}