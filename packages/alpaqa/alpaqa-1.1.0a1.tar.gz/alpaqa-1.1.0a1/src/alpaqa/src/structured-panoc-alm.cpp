#include <alpaqa/implementation/inner/directions/panoc/structured-lbfgs.tpp>
#include <alpaqa/implementation/inner/panoc.tpp>
#include <alpaqa/implementation/outer/alm.tpp>
#include <alpaqa/structured-panoc-alm.hpp>

namespace alpaqa {

// clang-format off
ALPAQA_EXPORT_TEMPLATE(class, PANOCSolver, StructuredLBFGSDirection<EigenConfigd>);
ALPAQA_IF_FLOAT(ALPAQA_EXPORT_TEMPLATE(class, PANOCSolver, StructuredLBFGSDirection<EigenConfigf>);)
ALPAQA_IF_LONGD(ALPAQA_EXPORT_TEMPLATE(class, PANOCSolver, StructuredLBFGSDirection<EigenConfigl>);)
ALPAQA_IF_QUADF(ALPAQA_EXPORT_TEMPLATE(class, PANOCSolver, StructuredLBFGSDirection<EigenConfigq>);)

ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, PANOCSolver<StructuredLBFGSDirection<EigenConfigd>>);
ALPAQA_IF_FLOAT(ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, PANOCSolver<StructuredLBFGSDirection<EigenConfigf>>);)
ALPAQA_IF_LONGD(ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, PANOCSolver<StructuredLBFGSDirection<EigenConfigl>>);)
ALPAQA_IF_QUADF(ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, PANOCSolver<StructuredLBFGSDirection<EigenConfigq>>);)
// clang-format on

} // namespace alpaqa