package dev.dres.run.score.scorer

import dev.dres.data.model.run.interfaces.TaskRun
import dev.dres.data.model.submissions.Submission
import dev.dres.data.model.template.team.TeamId
import dev.dres.data.model.submissions.VerdictStatus
import dev.dres.run.score.Scoreable
import jetbrains.exodus.database.TransientEntityStore
import kotlin.math.max

class KisTaskScorer(
    scoreable: Scoreable,
    private val maxPointsPerTask: Double = defaultmaxPointsPerTask,
    private val maxPointsAtTaskEnd: Double = defaultmaxPointsAtTaskEnd,
    private val penaltyPerWrongSubmission: Double = defaultpenaltyPerWrongSubmission,
    store: TransientEntityStore?
) : AbstractTaskScorer(scoreable, store) {

    constructor(run: TaskRun, parameters: Map<String, String>, store: TransientEntityStore?) : this(
        run,
        parameters.getOrDefault("maxPointsPerTask", "$defaultmaxPointsPerTask").toDoubleOrNull() ?: defaultmaxPointsPerTask,
        parameters.getOrDefault("maxPointsAtTaskEnd", "$defaultmaxPointsAtTaskEnd").toDoubleOrNull() ?: defaultmaxPointsAtTaskEnd,
        parameters.getOrDefault("penaltyPerWrongSubmission", "$defaultpenaltyPerWrongSubmission").toDoubleOrNull() ?: defaultpenaltyPerWrongSubmission,
        store
    )

    companion object {
        private const val defaultmaxPointsPerTask: Double = 100.0
        private const val defaultmaxPointsAtTaskEnd: Double = 50.0
        private const val defaultpenaltyPerWrongSubmission: Double = 10.0
    }

    /**
     * Computes and returns the scores for this [KisTaskScorer] based on a [Sequence] of [Submission]s.
     *
     * The sole use of this method is to keep the implementing classes unit-testable (irrespective of the database).
     *
     * @param submissions A [Sequence] of [Submission]s to obtain scores for.
     * @return A [Map] of [TeamId] to calculated task score.
     */
    override fun calculateScores(submissions: Sequence<Submission>): Map<TeamId, Double>  {
        val taskDuration = this.scoreable.duration.toDouble() * 1000.0
        val taskStartTime = this.scoreable.started ?: throw IllegalArgumentException("No task start time specified.")
        return this.scoreable.teams.associateWith { teamId ->
            val verdicts = submissions.filter { it.teamId == teamId }.sortedBy { it.timestamp }.flatMap { sub ->
                sub.answerSets().filter { (it.status() == VerdictStatus.CORRECT) or (it.status() == VerdictStatus.WRONG) or (it.status() == VerdictStatus.PARTIALLY_CORRECT)}
            }.toList()
            // Get max score where partially correct is treated as correct but get half of the score and half of penalty
            var score = 0.0
            var correct = 0
            var partiallyCorrect = 0
            var wrong = 0
            var firstCorrectIndex = -1
            var firstPartiallyCorrectIndex = -1
            for ((index, verdict) in verdicts.withIndex()) {
                when (verdict.status()) {
                    VerdictStatus.CORRECT -> {
                        correct++
                        if (firstCorrectIndex == -1) {
                            firstCorrectIndex = index
                        }
                    }
                    VerdictStatus.PARTIALLY_CORRECT -> {
                        partiallyCorrect++
                        if (firstPartiallyCorrectIndex == -1) {
                            firstPartiallyCorrectIndex = index
                        }
                    }
                    VerdictStatus.WRONG -> wrong++
                    else -> {}
                }
            }
            if (firstCorrectIndex != -1) {
                val timeFraction = 1.0 - (verdicts[firstCorrectIndex].submission.timestamp - taskStartTime) / taskDuration
                score = max(
                    0.0,
                    this.maxPointsAtTaskEnd +
                            ((maxPointsPerTask - maxPointsAtTaskEnd) * timeFraction) -
                            (firstCorrectIndex * penaltyPerWrongSubmission) //index of first correct submission is the same as number of not correct submissions
                )
            }
            if (firstPartiallyCorrectIndex != -1) {
                val timeFraction = 1.0 - (verdicts[firstPartiallyCorrectIndex].submission.timestamp - taskStartTime) / taskDuration
                score = max(
                    score,
                    (this.maxPointsAtTaskEnd +
                            ((maxPointsPerTask - maxPointsAtTaskEnd) * timeFraction) -
                            (firstPartiallyCorrectIndex * penaltyPerWrongSubmission)) / 2.0
                ) 
            }   
            // val firstCorrect = verdicts.indexOfFirst { it.status() == VerdictStatus.CORRECT }
            // val score = if (firstCorrect > -1) {
            //     val timeFraction = 1.0 - (verdicts[firstCorrect].submission.timestamp - taskStartTime) / taskDuration
            //     max(
            //         0.0,
            //         this.maxPointsAtTaskEnd +
            //                 ((maxPointsPerTask - maxPointsAtTaskEnd) * timeFraction) -
            //                 (firstCorrect * penaltyPerWrongSubmission) //index of first correct submission is the same as number of not correct submissions
            //     )
            // } else {
            //     0.0
            // }
            score
        }
    }
}