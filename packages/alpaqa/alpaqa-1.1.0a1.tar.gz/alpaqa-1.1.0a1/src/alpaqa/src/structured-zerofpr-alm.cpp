#include <alpaqa/implementation/inner/directions/panoc/structured-lbfgs.tpp>
#include <alpaqa/implementation/inner/zerofpr.tpp>
#include <alpaqa/implementation/outer/alm.tpp>
#include <alpaqa/structured-zerofpr-alm.hpp>

namespace alpaqa {

// clang-format off
ALPAQA_EXPORT_TEMPLATE(class, ZeroFPRSolver, StructuredLBFGSDirection<EigenConfigd>);
ALPAQA_IF_FLOAT(ALPAQA_EXPORT_TEMPLATE(class, ZeroFPRSolver, StructuredLBFGSDirection<EigenConfigf>);)
ALPAQA_IF_LONGD(ALPAQA_EXPORT_TEMPLATE(class, ZeroFPRSolver, StructuredLBFGSDirection<EigenConfigl>);)
ALPAQA_IF_QUADF(ALPAQA_EXPORT_TEMPLATE(class, ZeroFPRSolver, StructuredLBFGSDirection<EigenConfigq>);)

ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, ZeroFPRSolver<StructuredLBFGSDirection<EigenConfigd>>);
ALPAQA_IF_FLOAT(ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, ZeroFPRSolver<StructuredLBFGSDirection<EigenConfigf>>);)
ALPAQA_IF_LONGD(ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, ZeroFPRSolver<StructuredLBFGSDirection<EigenConfigl>>);)
ALPAQA_IF_QUADF(ALPAQA_EXPORT_TEMPLATE(class, ALMSolver, ZeroFPRSolver<StructuredLBFGSDirection<EigenConfigq>>);)
// clang-format on

} // namespace alpaqa