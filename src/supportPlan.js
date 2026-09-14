const stressLevelPlans = {
  low: {
    checkInIntervalHours: 24,
    actions: ['Maintain regular sleep schedule', 'Log one positive event before bed'],
  },
  medium: {
    checkInIntervalHours: 12,
    actions: ['Do a guided breathing cycle for 5 minutes', 'Take a 10-minute walk without notifications'],
  },
  high: {
    checkInIntervalHours: 4,
    actions: ['Run a grounding exercise (5-4-3-2-1)', 'Reach out to a trusted contact'],
  },
};

function inferStressLevel(score) {
  if (score >= 0.7) return 'high';
  if (score >= 0.4) return 'medium';
  return 'low';
}

function buildSupportPlan(payload) {
  const safeStressScore = Number.isFinite(payload.stressScore) ? payload.stressScore : 0.5;
  const normalizedStressScore = Math.max(0, Math.min(1, safeStressScore));
  const stressLevel = payload.stressLevel || inferStressLevel(normalizedStressScore);

  return {
    userId: payload.userId || 'anonymous',
    stressScore: normalizedStressScore,
    stressLevel,
    recommendedPlan: stressLevelPlans[stressLevel] || stressLevelPlans.medium,
    generatedAt: new Date().toISOString(),
    disclaimer:
      'This recommendation is not a medical diagnosis. Contact a qualified professional for urgent or clinical support.',
  };
}

module.exports = {
  buildSupportPlan,
};
