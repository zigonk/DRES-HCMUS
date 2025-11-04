package dev.dres.run.validation

import dev.dres.data.model.submissions.*
import dev.dres.run.validation.interfaces.AnswerSetValidator
import kotlinx.dnq.query.iterator

/**
 * A [AnswerSetValidator] class that validates textual submissions based on [Regex].
 *
 * @author Luca Rossetto
 * @author Ralph Gasser
 * @version 2.0.0
 */
class TextAnswerSetValidator(targets: List<String>) : AnswerSetValidator {

    override val deferring = false

    /**
     * Transforms the targets to [Regex]s.
     * There is the convention introduced, that targets padded in backslashes (single) (\)
     * are interpreted as regular expressions and the enclosing backslashes are removed.
     * Ending a target string with '\i' will cause capitalization to be ignored.
     * Regular Java pattern compilation rules apply.
     * If the enclosing backslashes are missing, then the target is treated as a literal string.
     *
     * [RegexOption.CANON_EQ] is activated for both, regex and literals.
     */
    private val regex = targets.map {
        when {
            it.startsWith("\\") && it.endsWith("\\") -> Regex(it.substring(1, it.length - 1), RegexOption.CANON_EQ)
            it.startsWith("\\") && it.endsWith("\\i") ->Regex(it.substring(1, it.length - 2), setOf(RegexOption.CANON_EQ, RegexOption.IGNORE_CASE))
            else -> Regex(it, setOf(RegexOption.CANON_EQ, RegexOption.LITERAL))
        }
    }

        private fun parsingTrakeAnswer(answer: String?): Pair<String?, List<Int>?> {
            if (answer == null) {
                return Pair(null, null)
            }
            val parts = answer.split("-")
            if (parts.size != 2) {
                return Pair(null, null)
            }
            val videoId = parts[0]
            val framesPart = parts[1]
            val frames = framesPart.split(",").mapNotNull { it.trim().toIntOrNull() }
            if (frames.isEmpty()) {
                return Pair(videoId, null)
            }
            return Pair(videoId, frames)
        }

    /**
     * Validates the [DbAnswerSet] and updates its [DBVerdictStatus].
     *
     * Usually requires an ongoing transaction.
     *
     * @param answerSet The [DbAnswerSet] to validate.
     */
    override fun validate(answerSet: DbAnswerSet) {
        /* Basically, we assume that the DBAnswerSet is wrong. */
        answerSet.status = DbVerdictStatus.WRONG
        // Get task type by 2 first letters "QA" or "TR".
        val taskType = regex.firstOrNull()?.pattern?.substring(0,2)
        if (taskType == null || (taskType != "QA" && taskType != "TR")) {
            return
        }
        var matchedFrames = 0;
        var totalFrames = 0
        /* Now we check all the answers. */
        for (answer in answerSet.answers) {
            /* Perform sanity checks. */
            val text = answer.text
            // If taskType is "QA", we do normal validation.
            if (taskType == "QA") {
                // Answer in format <ANSWER>-<VIDEO_ID>-<TIME(ms)>
                // Ground truth in format <ANSWER>-<VIDEO_ID>-<START>-<END>
                if (answer.type != DbAnswerType.TEXT || text == null) {
                    return
                }
                val panswer = text.substring(3, text.length)
                val answerParts = panswer.split("-")
                if (answerParts.size != 3) {
                    return
                }
                val submittedAnswer = answerParts[0]
                val submittedVideoId = answerParts[1]
                val submittedTime = answerParts[2].toIntOrNull()
                if (submittedTime == null) {
                    return
                }
                
                // Parse ground truth pattern
                val gtPattern = regex.first().pattern
                val gtParts = gtPattern.split("-")
                if (gtParts.size != 4) {
                    return
                }
                val gtAnswer = gtParts[0]
                val gtVideoId = gtParts[1]
                val gtStart = gtParts[2].toIntOrNull()
                val gtEnd = gtParts[3].toIntOrNull()
                if (gtStart == null || gtEnd == null) {
                    return
                }
                
                // Check if answer, video ID match and time is within range
                if (submittedAnswer == gtAnswer && submittedVideoId == gtVideoId && submittedTime in gtStart..gtEnd) {
                    answerSet.status = DbVerdictStatus.CORRECT
                    return
                }
            }
            else if (taskType == "TR") { // If taskType is "TR", we do split
                // Parsing the answer in format <VIDEO_ID>-<FRAME1,FRAME2,...>
                val (videoId, frames) = parsingTrakeAnswer(text?.substring(3, text.length))
                // Parsing ground truth in format <VIDEO_ID>-<FRAME1,FRAME2,...>
                val (gtVideoId, gtFrames) = parsingTrakeAnswer(regex.first().pattern)
                if (answer.type != DbAnswerType.TEXT || text == null || videoId == null || frames == null || gtVideoId == null || gtFrames == null) {
                    return
                }
                // Check if video IDs match.
                if (videoId != gtVideoId) {
                    return
                }
                // Check frame-by-frame in order with tolerance of 12 frames.
                val tolerance = 12
                totalFrames = frames.size
                for (i in 1..frames.size) {
                    val frame = frames[i - 1]
                    val gtFrame = gtFrames.getOrNull(i - 1)
                    if (gtFrame == null || frame !in (gtFrame - tolerance)..(gtFrame + tolerance)) {
                        continue
                    } else {
                        matchedFrames++
                    }
                }
            }
        }
        if (taskType == "TR") {
            val matchRatio = if (totalFrames == 0) 0.0 else matchedFrames.toDouble() / totalFrames
            answerSet.status = when {
                matchRatio >= 1.0 -> DbVerdictStatus.CORRECT
                matchRatio >= 0.5 -> DbVerdictStatus.PARTIALLY_CORRECT
                else -> DbVerdictStatus.WRONG
            }
            return
        }
        /* If code reaches this point, the [DbAnswerSet] is correct. */
        answerSet.status = DbVerdictStatus.CORRECT
    }
}
