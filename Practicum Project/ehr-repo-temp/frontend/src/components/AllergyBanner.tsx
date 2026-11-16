import "./allergyBanner.css";

interface Allergy {
  substance: string;
  reaction: string | null;
}

interface AllergyBannerProps {
  allergies: Allergy[];
}

// Strip shown at the top of a patient's chart so allergies are seen before
// anything else. An empty list only means nothing is recorded (not a
// confirmed "no known drug allergies"), so the empty state says to verify.
export function AllergyBanner({ allergies }: AllergyBannerProps) {
  if (allergies.length === 0) {
    return (
      <div className="allergy-banner allergy-banner--none" role="status">
        <strong className="allergy-banner__label">Allergies</strong>
        <span>No allergies on file. Verify with the patient.</span>
      </div>
    );
  }

  return (
    <div className="allergy-banner allergy-banner--alert" role="alert">
      <strong className="allergy-banner__label">
        ⚠ Allergies ({allergies.length})
      </strong>
      <ul className="allergy-banner__list">
        {allergies.map((a, i) => (
          <li key={i}>
            <strong>{a.substance}</strong>
            {a.reaction && <span> · {a.reaction}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
