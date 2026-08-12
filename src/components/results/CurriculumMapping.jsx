import UnitMapping from "./UnitMapping";

export default function CurriculumMapping({
  result,
  mapping,
}) {
  return (
    <UnitMapping
      result={result}
      mapping={
        mapping ||
        result?.curriculum_mapping
      }
    />
  );
}