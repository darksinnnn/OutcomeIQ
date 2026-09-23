import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { outcomeIQApi } from '../services/api';
import { useUIStore } from '../stores/uiStore';
import { PageHeader } from '../components/common/PageHeader';
import { StateWrapper } from '../components/common/StateWrapper';
import { PassportCapabilityBar } from '../components/modules/PassportCapabilityBar';
import { UserCheck, ShieldCheck, Award, MessageSquare, CheckCircle, Info, X } from 'lucide-react';

export const OperatorPassportPage: React.FC = () => {
  const { operatorId } = useParams<{ operatorId?: string }>();
  const activeOpId = operatorId || 'OP-101';

  const contestingItem = useUIStore((state) => state.contestingItem);
  const setContestingItem = useUIStore((state) => state.setContestingItem);

  const [contestNote, setContestNote] = useState('');
  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);

  const { data: passportData, isLoading, isError, refetch } = useQuery({
    queryKey: ['operator-passport', activeOpId],
    queryFn: () => outcomeIQApi.getOperatorPassport(activeOpId),
  });

  const handleContestSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittedMessage(`Annotation submitted for ${contestingItem?.context}. Record updated for operator review.`);
    setTimeout(() => {
      setSubmittedMessage(null);
      setContestingItem(null);
      setContestNote('');
    }, 2500);
  };

  return (
    <div>
      <PageHeader
        title={`Operator Capability Passport — ${passportData?.operator.name || activeOpId}`}
        subtitle="Demonstrated capability evidence in specific context (task + soil + weather) — NOT a surveillance score."
      />

      <StateWrapper isLoading={isLoading} isError={isError} onRetry={refetch}>
        {passportData && (
          <div className="space-y-6">
            {/* Operator Profile Banner */}
            <div className="bg-panel border border-hairline rounded-md p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-sm bg-accent/15 text-accent font-display font-bold text-lg flex items-center justify-center border border-accent/30">
                  {passportData.operator.name.split(' ').map((n) => n[0]).join('')}
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <h2 className="font-display text-xl font-bold text-text-primary">
                      {passportData.operator.name}
                    </h2>
                    <span className="text-xs font-mono text-text-muted px-2 py-0.5 rounded-sm bg-base border border-hairline">
                      {passportData.operator.id}
                    </span>
                  </div>
                  <p className="text-xs font-body text-text-secondary">
                    Experience: <strong className="text-text-primary font-medium">{passportData.operator.experience_years} years</strong> heavy machine operations.
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {passportData.operator.certifications?.map((cert, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] font-display px-2.5 py-1 rounded-sm bg-elevated border border-hairline text-text-secondary flex items-center gap-1.5"
                  >
                    <Award className="w-3.5 h-3.5 text-accent" />
                    {cert}
                  </span>
                ))}
              </div>
            </div>

            {/* Evidence Framing Note */}
            <div className="bg-panel/70 border border-hairline p-4 rounded-md flex items-start gap-3">
              <Info className="w-5 h-5 text-data-blue shrink-0 mt-0.5" />
              <div className="text-xs font-body text-text-secondary space-y-1">
                <p>
                  <strong className="text-text-primary font-medium">Trust & Safety Standard:</strong> Capability is measured exclusively by demonstrated contextual evidence (sample count, historical duration delta, quality pass rate). Low confidence indicates a small sample size in that specific context (e.g., wet clay), never a personal skill judgment.
                </p>
              </div>
            </div>

            {/* Context Capability Bars */}
            <div className="space-y-4">
              <h3 className="font-display font-semibold text-sm text-text-primary uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-accent" />
                Demonstrated Capability Evidence Records ({passportData.evidence_records.length})
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {passportData.evidence_records.map((record) => (
                  <PassportCapabilityBar key={record.id} record={record} />
                ))}
              </div>
            </div>
          </div>
        )}
      </StateWrapper>

      {/* Contestability / Annotation Modal */}
      {contestingItem && (
        <div className="fixed inset-0 z-50 bg-base/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-elevated border border-hairline rounded-md max-w-md w-full p-6 space-y-4 shadow-elevated">
            <div className="flex items-center justify-between border-b border-hairline pb-3">
              <h3 className="font-display font-semibold text-sm text-text-primary flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-accent" />
                Annotate / Contest Evidence Record
              </h3>
              <button
                onClick={() => setContestingItem(null)}
                className="text-text-muted hover:text-text-primary"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {submittedMessage ? (
              <div className="bg-status-green/15 border border-status-green/30 text-status-green p-4 rounded-sm text-xs font-display flex items-center gap-2">
                <CheckCircle className="w-4 h-4 shrink-0" />
                <span>{submittedMessage}</span>
              </div>
            ) : (
              <form onSubmit={handleContestSubmit} className="space-y-4">
                <p className="text-xs text-text-secondary font-body">
                  Operator or Supervisor note for context: <strong className="text-text-primary">{contestingItem.context}</strong>
                </p>
                <div>
                  <label className="text-[11px] font-display text-text-muted uppercase tracking-wider block mb-1">
                    Annotation / Contest Reason
                  </label>
                  <textarea
                    required
                    value={contestNote}
                    onChange={(e) => setContestNote(e.target.value)}
                    placeholder="e.g. Unannounced site haul delay; bucket teeth replaced mid-shift."
                    className="w-full bg-base border border-hairline rounded-sm p-3 text-xs text-text-primary font-body focus:outline-none focus:ring-2 focus:ring-accent h-24"
                  />
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setContestingItem(null)}
                    className="px-3 py-1.5 bg-panel hover:bg-hairline text-text-secondary text-xs font-display rounded-sm border border-hairline"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 bg-accent hover:bg-accent/90 text-base font-display font-semibold text-xs rounded-sm"
                  >
                    Submit Annotation
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
