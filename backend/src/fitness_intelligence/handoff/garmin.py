"""Manual Garmin Connect entry from the exact elapsed-time E4.1 prescription."""

from typing import Literal

from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning.prescriptions import Target

from .prescription import Handoff, PrescriptionExport, effort_text, target_text


class GarminWorksheet(Handoff):
    policy: Literal["garmin-connect-worksheet.v1"] = "garmin-connect-worksheet.v1"
    repeat_instructions: tuple[str, ...]
    steps: tuple[f.Step, ...]
    workout_seconds: Target[int]
    preparation_seconds: int
    reservation_seconds: int

    def render(self) -> str:
        s = self.source
        session = s.session
        lines = [
            f"Garmin Connect · Run · {session.template} ({session.prescription.role})",
            f"{s.approval} · {self.classification} · local worksheet only",
            f"Week {s.week} · {s.local_start} ({s.zone})",
            f"Cycle {s.cycle} · revision {s.revision} · occurrence {session.occurrence}",
            f"Prescription SHA-256 {s.prescription_sha256}",
            f"{self.policy} · export SHA-256 {self.digest()}",
            f"Elapsed workout {target_text(self.workout_seconds)} s · "
            f"prepare separately {self.preparation_seconds} s · "
            f"reserve {self.reservation_seconds} s",
            *self.repeat_instructions,
            "Expanded steps · use open intensity and copy each effort cue",
        ]
        for index, step in enumerate(self.steps, 1):
            lines.append(
                f"{index}. {step.purpose} · {target_text(step.seconds)} s · "
                f"{effort_text(step.effort)}"
            )
        if session.prescription.notes:
            lines.append(session.prescription.notes)
        lines.extend(self.limitations)
        lines.append(
            "In Connect, create a Run workout and check the expanded sequence above. "
            "Add to Calendar on the displayed local date. Sync and compare the watch calendar "
            "entry, step order, timing and visible cues before starting."
        )
        return "\n".join(lines)


def garmin_worksheet(source: PrescriptionExport) -> GarminWorksheet:
    p = source.session.prescription
    if not isinstance(p, f.Running):
        raise ValueError("Garmin running worksheet requires a running prescription")
    repeats = []
    offset = 1
    for segment in p.segments:
        if isinstance(segment, f.Repeat):
            length = len(segment.expand())
            final = "one explicit final recovery" if segment.final_recovery else "no final recovery"
            repeats.append(
                f"Steps {offset}–{offset + length - 1}: {segment.count} work bouts, "
                f"{segment.count - 1} between-bout recoveries, {final}."
            )
            offset += length
        else:
            offset += 1
    steps = p.steps
    limits = ["Interpret step RPE and caps manually. No pace or heart-rate target is prescribed."]
    if any(step.seconds.low != step.seconds.high for step in steps):
        limits.append(
            "For each duration range, use a lap-button end and the displayed time cue. "
            "The athlete chooses within the range. A fixed timer removes this choice."
        )
    return GarminWorksheet(
        source=source,
        classification="usable-with-disclosed-limitations",
        limitations=(*source.historical_limitations, *limits),
        repeat_instructions=tuple(repeats),
        steps=steps,
        workout_seconds=p.duration,
        preparation_seconds=p.preparation_seconds,
        reservation_seconds=p.reserved_seconds,
    )
