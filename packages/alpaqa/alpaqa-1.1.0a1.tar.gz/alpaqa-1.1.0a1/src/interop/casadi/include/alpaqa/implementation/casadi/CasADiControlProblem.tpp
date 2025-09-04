#pragma once

#include <alpaqa/casadi/CasADiControlProblem.hpp>
#include <alpaqa/casadi/CasADiFunctionWrapper.hpp>
#include <alpaqa/casadi/casadi-namespace.hpp>
#include <alpaqa/config/config.hpp>
#include <alpaqa/util/span.hpp>
#include <alpaqa/util/sparse-ops.hpp>
#include "CasADiLoader-util.hpp"
#include <guanaqo/dl-flags.hpp>
#include <guanaqo/io/csv.hpp>
#include <guanaqo/not-implemented.hpp>

#include <Eigen/Sparse>

#if ALPAQA_WITH_EXTERNAL_CASADI
#include <casadi/core/external.hpp>
#endif

#include <fstream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <type_traits>

namespace alpaqa {
BEGIN_ALPAQA_CASADI_LOADER_NAMESPACE

namespace fs = std::filesystem;

namespace casadi_loader {

using namespace alpaqa::casadi_loader;

template <Config Conf>
struct CasADiControlFunctionsWithParam {
    USING_ALPAQA_CONFIG(Conf);

    static constexpr bool WithParam = true;
    length_t nx, nu, nh, nh_N, nc, nc_N, p;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> f;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> jac_f;
    CasADiFunctionEvaluator<Conf, 3 + WithParam, 1> grad_f_prod;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> h;
    CasADiFunctionEvaluator<Conf, 1 + WithParam, 1> h_N;
    CasADiFunctionEvaluator<Conf, 1 + WithParam, 1> l;
    CasADiFunctionEvaluator<Conf, 1 + WithParam, 1> l_N;

    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> qr;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> q_N;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> Q;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> Q_N;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> R;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> S;

    CasADiFunctionEvaluator<Conf, 1 + WithParam, 1> c;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> grad_c_prod;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> gn_hess_c;

    CasADiFunctionEvaluator<Conf, 1 + WithParam, 1> c_N;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> grad_c_prod_N;
    CasADiFunctionEvaluator<Conf, 2 + WithParam, 1> gn_hess_c_N;

    template <class Loader>
        requires requires(Loader &&loader, const char *name) {
            { loader(name) } -> std::same_as<casadi::Function>;
            { loader.format_name(name) } -> std::same_as<std::string>;
        }
    static std::unique_ptr<CasADiControlFunctionsWithParam>
    load(Loader &&loader) {
        length_t nx, nu, nh, nh_N, nc, nc_N, p;
        auto load_f = [&]() -> CasADiFunctionEvaluator<Conf, 3, 1> {
            casadi::Function ffun = loader("f");
            using namespace std::literals::string_literals;
            if (ffun.n_in() != 3)
                throw invalid_argument_dimensions(
                    "Invalid number of input arguments: got "s +
                    std::to_string(ffun.n_in()) + ", should be 3.");
            if (ffun.n_out() != 1)
                throw invalid_argument_dimensions(
                    "Invalid number of output arguments: got "s +
                    std::to_string(ffun.n_in()) + ", should be 1.");
            nx = static_cast<length_t>(ffun.size1_in(0));
            nu = static_cast<length_t>(ffun.size1_in(1));
            p  = static_cast<length_t>(ffun.size1_in(2));
            CasADiFunctionEvaluator<Conf, 3, 1> f{std::move(ffun)};
            f.validate_dimensions({dim(nx, 1), dim(nu, 1), dim(p, 1)},
                                  {dim(nx, 1)});
            return f;
        };
        auto load_h = [&]() -> CasADiFunctionEvaluator<Conf, 3, 1> {
            casadi::Function hfun = loader("h");
            using namespace std::literals::string_literals;
            if (hfun.n_in() != 3)
                throw invalid_argument_dimensions(
                    "Invalid number of input arguments: got "s +
                    std::to_string(hfun.n_in()) + ", should be 3.");
            if (hfun.n_out() != 1)
                throw invalid_argument_dimensions(
                    "Invalid number of output arguments: got "s +
                    std::to_string(hfun.n_in()) + ", should be 1.");
            nh = static_cast<length_t>(hfun.size1_out(0));
            CasADiFunctionEvaluator<Conf, 3, 1> h{std::move(hfun)};
            h.validate_dimensions({dim(nx, 1), dim(nu, 1), dim(p, 1)},
                                  {dim(nh, 1)});
            return h;
        };
        auto load_h_N = [&]() -> CasADiFunctionEvaluator<Conf, 2, 1> {
            casadi::Function hfun = loader("h_N");
            using namespace std::literals::string_literals;
            if (hfun.n_in() != 2)
                throw invalid_argument_dimensions(
                    "Invalid number of input arguments: got "s +
                    std::to_string(hfun.n_in()) + ", should be 2.");
            if (hfun.n_out() != 1)
                throw invalid_argument_dimensions(
                    "Invalid number of output arguments: got "s +
                    std::to_string(hfun.n_in()) + ", should be 1.");
            nh_N = static_cast<length_t>(hfun.size1_out(0));
            CasADiFunctionEvaluator<Conf, 2, 1> h{std::move(hfun)};
            h.validate_dimensions({dim(nx, 1), dim(p, 1)}, {dim(nh_N, 1)});
            return h;
        };
        auto load_c = [&]() -> CasADiFunctionEvaluator<Conf, 2, 1> {
            casadi::Function cfun = loader("c");
            using namespace std::literals::string_literals;
            if (cfun.n_in() != 2)
                throw invalid_argument_dimensions(
                    "Invalid number of input arguments: got "s +
                    std::to_string(cfun.n_in()) + ", should be 2.");
            if (cfun.n_out() != 1)
                throw invalid_argument_dimensions(
                    "Invalid number of output arguments: got "s +
                    std::to_string(cfun.n_in()) + ", should be 1.");
            nc = static_cast<length_t>(cfun.size1_out(0));
            CasADiFunctionEvaluator<Conf, 2, 1> c{std::move(cfun)};
            c.validate_dimensions({dim(nx, 1), dim(p, 1)}, {dim(nc, 1)});
            return c;
        };
        auto load_c_N = [&]() -> CasADiFunctionEvaluator<Conf, 2, 1> {
            casadi::Function cfun = loader("c_N");
            using namespace std::literals::string_literals;
            if (cfun.n_in() != 2)
                throw invalid_argument_dimensions(
                    "Invalid number of input arguments: got "s +
                    std::to_string(cfun.n_in()) + ", should be 2.");
            if (cfun.n_out() != 1)
                throw invalid_argument_dimensions(
                    "Invalid number of output arguments: got "s +
                    std::to_string(cfun.n_in()) + ", should be 1.");
            nc_N = static_cast<length_t>(cfun.size1_out(0));
            CasADiFunctionEvaluator<Conf, 2, 1> c{std::move(cfun)};
            c.validate_dimensions({dim(nx, 1), dim(p, 1)}, {dim(nc_N, 1)});
            return c;
        };
        // Load the functions "f", "h", and "c" to determine the unknown dimensions.
        auto f   = wrap_load(loader, "f", load_f);
        auto h   = wrap_load(loader, "h", load_h);
        auto h_N = wrap_load(loader, "h_N", load_h_N);
        auto c   = wrap_load(loader, "c", load_c);
        auto c_N = wrap_load(loader, "c_N", load_c_N);

        auto self = std::make_unique<CasADiControlFunctionsWithParam<Conf>>(
            CasADiControlFunctionsWithParam<Conf>{
                .nx    = nx,
                .nu    = nu,
                .nh    = nh,
                .nh_N  = nh_N,
                .nc    = nc,
                .nc_N  = nc_N,
                .p     = p,
                .f     = std::move(f),
                .jac_f = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "jacobian_f", dims(nx, nu, p),
                    dims(dim(nx, nx + nu))),
                .grad_f_prod =
                    wrapped_load<CasADiFunctionEvaluator<Conf, 4, 1>>(
                        loader, "grad_f_prod", dims(nx, nu, p, nx),
                        dims(nx + nu)),
                .h   = std::move(h),
                .h_N = std::move(h_N),
                .l   = wrapped_load<CasADiFunctionEvaluator<Conf, 2, 1>>(
                    loader, "l", dims(nh, p), dims(1)),
                .l_N = wrapped_load<CasADiFunctionEvaluator<Conf, 2, 1>>(
                    loader, "l_N", dims(nh_N, p), dims(1)),
                .qr = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "qr", dims(nx + nu, nh, p), dims(nx + nu)),
                .q_N = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "q_N", dims(nx, nh_N, p), dims(nx)),
                .Q = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "Q", dims(nx + nu, nh, p), dims(dim{nx, nx})),
                .Q_N = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "Q_N", dims(nx, nh_N, p), dims(dim{nx, nx})),
                .R = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "R", dims(nx + nu, nh, p), dims(dim{nu, nu})),
                .S = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "S", dims(nx + nu, nh, p), dims(dim{nu, nx})),
                .c = std::move(c),
                .grad_c_prod =
                    wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                        loader, "grad_c_prod", dims(nx, p, nc), dims(nx)),
                .gn_hess_c = wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                    loader, "gn_hess_c", dims(nx, p, nc), dims(dim{nx, nx})),
                .c_N = std::move(c_N),
                .grad_c_prod_N =
                    wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                        loader, "grad_c_prod_N", dims(nx, p, nc_N), dims(nx)),
                .gn_hess_c_N =
                    wrapped_load<CasADiFunctionEvaluator<Conf, 3, 1>>(
                        loader, "gn_hess_c_N", dims(nx, p, nc_N),
                        dims(dim{nx, nx})),
            });
        return self;
    }
};

} // namespace casadi_loader

template <Config Conf>
CasADiControlProblem<Conf>::CasADiControlProblem(const std::string &filename,
                                                 length_t N,
                                                 DynamicLoadFlags dl_flags)
    : N{N} {

    struct {
        const std::string &filename;
        DynamicLoadFlags dl_flags;
        auto operator()(const std::string &name) const {
#if ALPAQA_WITH_EXTERNAL_CASADI
            return casadi::external(name, filename);
#else
            return casadi::external(name, filename, dl_flags);
#endif
        }
        auto format_name(const std::string &name) const {
            return filename + ':' + name;
        }
    } loader{filename, dl_flags};
    impl = casadi_loader::CasADiControlFunctionsWithParam<Conf>::load(loader);

    this->nx     = impl->nx;
    this->nu     = impl->nu;
    this->nh     = impl->nh;
    this->nh_N   = impl->nh_N;
    this->nc     = impl->nc;
    this->nc_N   = impl->nc_N;
    this->x_init = vec::Constant(nx, alpaqa::NaN<Conf>);
    this->param  = vec::Constant(impl->p, alpaqa::NaN<Conf>);
    this->U      = Box{nu};
    this->D      = Box{nc};
    this->D_N    = Box{nc_N};

    auto n_work = std::max({
        impl->Q.fun.sparsity_out(0).nnz(),
        impl->Q_N.fun.sparsity_out(0).nnz(),
        impl->gn_hess_c.fun.sparsity_out(0).nnz(),
        impl->gn_hess_c_N.fun.sparsity_out(0).nnz(),
    });
    this->work  = vec::Constant(static_cast<length_t>(n_work), NaN<Conf>);

    auto bounds_filepath = fs::path{filename}.replace_extension("csv");
    if (fs::exists(bounds_filepath))
        load_numerical_data(bounds_filepath);
}

template <Config Conf>
void CasADiControlProblem<Conf>::load_numerical_data(
    const std::filesystem::path &filepath, char sep) {
    // Open data file
    std::ifstream data_file{filepath};
    if (!data_file)
        throw std::runtime_error("Unable to open data file \"" +
                                 filepath.string() + '"');

    // Helper function for reading single line of (float) data
    index_t line        = 0;
    auto wrap_data_load = [&](std::string_view name, auto &v,
                              bool fixed_size = true) {
        using namespace guanaqo::io;
        try {
            ++line;
            if (data_file.peek() == '\n') // Ignore empty lines
                return static_cast<void>(data_file.get());
            if (fixed_size) {
                csv_read_row(data_file, as_span(v), sep);
            } else { // Dynamic size
                auto s = csv_read_row_std_vector<real_t>(data_file, sep);
                v      = as_vec(std::span{s});
            }
        } catch (csv_read_error &e) {
            // Transform any errors in something more readable
            throw std::runtime_error("Unable to read " + std::string(name) +
                                     " from data file \"" + filepath.string() +
                                     ':' + std::to_string(line) +
                                     "\": " + e.what());
        }
    };
    // Helper function for reading a single value
    auto read_single = [&](std::string_view name, auto &v) {
        data_file >> v;
        if (!data_file)
            throw std::runtime_error("Unable to read " + std::string(name) +
                                     " from data file \"" + filepath.string() +
                                     ':' + std::to_string(line) + '"');
    };
    wrap_data_load("U.lower", this->U.lower);
    wrap_data_load("U.upper", this->U.upper);
    wrap_data_load("D.lower", this->D.lower);
    wrap_data_load("D.upper", this->D.upper);
    wrap_data_load("D_N.lower", this->D_N.lower);
    wrap_data_load("D_N.upper", this->D_N.upper);
    wrap_data_load("x_init", this->x_init);
    wrap_data_load("param", this->param);
    // Penalty/ALM split is a single integer
    read_single("penalty_alm_split", this->penalty_alm_split);
    read_single("penalty_alm_split_N", this->penalty_alm_split_N);
}

template <Config Conf>
CasADiControlProblem<Conf>::CasADiControlProblem(const CasADiControlProblem &) =
    default;
template <Config Conf>
CasADiControlProblem<Conf> &
CasADiControlProblem<Conf>::operator=(const CasADiControlProblem &) = default;

template <Config Conf>
CasADiControlProblem<Conf>::CasADiControlProblem(
    CasADiControlProblem &&) noexcept = default;
template <Config Conf>
CasADiControlProblem<Conf> &CasADiControlProblem<Conf>::operator=(
    CasADiControlProblem &&) noexcept = default;

template <Config Conf>
CasADiControlProblem<Conf>::~CasADiControlProblem() = default;

template <Config Conf>
void CasADiControlProblem<Conf>::eval_f(index_t, crvec x, crvec u,
                                        rvec fxu) const {
    assert(x.size() == nx);
    assert(u.size() == nu);
    assert(fxu.size() == nx);
    impl->f({x.data(), u.data(), param.data()}, {fxu.data()});
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_jac_f(index_t, crvec x, crvec u,
                                            rmat J_fxu) const {
    assert(x.size() == nx);
    assert(u.size() == nu);
    assert(J_fxu.rows() == nx);
    assert(J_fxu.cols() == nx + nu);
    impl->jac_f({x.data(), u.data(), param.data()}, {J_fxu.data()});
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_grad_f_prod(index_t, crvec x, crvec u,
                                                  crvec p,
                                                  rvec grad_fxu_p) const {
    assert(x.size() == nx);
    assert(u.size() == nu);
    assert(p.size() == nx);
    assert(grad_fxu_p.size() == nx + nu);
    impl->grad_f_prod({x.data(), u.data(), param.data(), p.data()},
                      {grad_fxu_p.data()});
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_h(index_t, crvec x, crvec u,
                                        rvec h) const {
    assert(x.size() == nx);
    assert(u.size() == nu);
    assert(h.size() == nh);
    impl->h({x.data(), u.data(), param.data()}, {h.data()});
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_h_N(crvec x, rvec h) const {
    assert(x.size() == nx);
    assert(h.size() == nh_N);
    impl->h_N({x.data(), param.data()}, {h.data()});
}
template <Config Conf>
auto CasADiControlProblem<Conf>::eval_l(index_t, crvec h) const -> real_t {
    assert(h.size() == nh);
    real_t l;
    impl->l({h.data(), param.data()}, {&l});
    return l;
}
template <Config Conf>
auto CasADiControlProblem<Conf>::eval_l_N(crvec h) const -> real_t {
    assert(h.size() == nh_N);
    real_t l;
    impl->l_N({h.data(), param.data()}, {&l});
    return l;
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_qr(index_t, crvec xu, crvec h,
                                         rvec qr) const {
    assert(xu.size() == nx + nu);
    assert(h.size() == nh);
    assert(qr.size() == nx + nu);
    impl->qr({xu.data(), h.data(), param.data()}, {qr.data()});
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_q_N(crvec x, crvec h, rvec q) const {
    assert(x.size() == nx);
    assert(h.size() == nh_N);
    assert(q.size() == nx);
    impl->q_N({x.data(), h.data(), param.data()}, {q.data()});
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_Q(index_t, crvec xu, crvec h,
                                            rmat Q) const {
    assert(xu.size() == nx + nu);
    assert(h.size() == nh);
    assert(Q.rows() == nx);
    assert(Q.cols() == nx);
    impl->Q({xu.data(), h.data(), param.data()}, {work.data()});
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    auto &&sparse = impl->Q.fun.sparsity_out(0);
    if (sparse.is_dense())
        Q += cmmat{work.data(), nx, nx};
    else
        Q += cmspmat{
            nx,
            nx,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
}
template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_Q_N(crvec x, crvec h, rmat Q) const {
    assert(x.size() == nx);
    assert(h.size() == nh_N);
    assert(Q.rows() == nx);
    assert(Q.cols() == nx);
    impl->Q_N({x.data(), h.data(), param.data()}, {work.data()});
    auto &&sparse = impl->Q_N.fun.sparsity_out(0);
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    if (sparse.is_dense())
        Q += cmmat{work.data(), nx, nx};
    else
        Q += cmspmat{
            nx,
            nx,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_R_masked(index_t, crvec xu, crvec h,
                                                   crindexvec mask, rmat R,
                                                   rvec work) const {
    auto &&sparse = impl->R.fun.sparsity_out(0);
    assert(xu.size() == nx + nu);
    assert(h.size() == nh);
    assert(R.rows() <= nu);
    assert(R.cols() <= nu);
    assert(R.rows() == mask.size());
    assert(R.cols() == mask.size());
    assert(work.size() >= static_cast<length_t>(sparse.nnz()));
    impl->R({xu.data(), h.data(), param.data()}, {work.data()});
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    if (sparse.is_dense()) {
        cmmat R_full{work.data(), nu, nu};
        R += R_full(mask, mask);
    } else {
        cmspmat R_full{
            nu,
            nu,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
        util::sparse_add_masked(R_full, R, mask);
    }
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_S_masked(index_t, crvec xu, crvec h,
                                                   crindexvec mask, rmat S,
                                                   rvec work) const {
    auto &&sparse = impl->S.fun.sparsity_out(0);
    assert(xu.size() == nx + nu);
    assert(h.size() == nh);
    assert(S.rows() <= nu);
    assert(S.rows() == mask.size());
    assert(S.cols() == nx);
    assert(work.size() >= static_cast<length_t>(sparse.nnz()));
    impl->S({xu.data(), h.data(), param.data()}, {work.data()});
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    using Eigen::indexing::all;
    if (sparse.is_dense()) {
        cmmat S_full{work.data(), nu, nx};
        S += S_full(mask, all);
    } else {
        cmspmat S_full{
            nu,
            nx,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
        util::sparse_add_masked_rows(S_full, S, mask);
    }
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_R_prod_masked(index_t, crvec, crvec,
                                                        crindexvec mask_J,
                                                        crindexvec mask_K,
                                                        crvec v, rvec out,
                                                        rvec work) const {
    auto &&sparse = impl->R.fun.sparsity_out(0);
    assert(v.size() == nu);
    assert(out.size() == mask_J.size());
    assert(work.size() >= static_cast<length_t>(sparse.nnz()));
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    if (sparse.is_dense()) {
        auto R = cmmat{work.data(), nu, nu};
        out.noalias() += R(mask_J, mask_K) * v(mask_K);
    } else {
        cmspmat R{
            nu,
            nu,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
        // out += R_full(mask_J,mask_K) * v(mask_K);
        util::sparse_matvec_add_masked_rows_cols(R, v, out, mask_J, mask_K);
    }
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_S_prod_masked(index_t, crvec, crvec,
                                                        crindexvec mask_K,
                                                        crvec v, rvec out,
                                                        rvec work) const {
    auto &&sparse = impl->S.fun.sparsity_out(0);
    assert(v.size() == nu);
    assert(out.size() == nx);
    assert(work.size() >= static_cast<length_t>(sparse.nnz()));
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    using Eigen::indexing::all;
    if (sparse.is_dense()) {
        auto Sᵀ = cmmat{work.data(), nu, nx}.transpose();
        out.noalias() += Sᵀ(all, mask_K) * v(mask_K);
    } else {
        cmspmat S{
            nu,
            nx,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
        // out += S(mask_K,:)ᵀ * v(mask_K);
        util::sparse_matvec_add_transpose_masked_rows(S, v, out, mask_K);
    }
}

template <Config Conf>
auto CasADiControlProblem<Conf>::get_R_work_size() const -> length_t {
    auto &&sparse = impl->R.fun.sparsity_out(0);
    return static_cast<length_t>(sparse.nnz());
}

template <Config Conf>
auto CasADiControlProblem<Conf>::get_S_work_size() const -> length_t {
    auto &&sparse = impl->S.fun.sparsity_out(0);
    return static_cast<length_t>(sparse.nnz());
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_constr(index_t, crvec x, rvec c) const {
    if (nc == 0)
        return;
    assert(x.size() == nx);
    assert(c.size() == nc);
    impl->c({x.data(), param.data()}, {c.data()});
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_grad_constr_prod(index_t, crvec x,
                                                       crvec p,
                                                       rvec grad_cx_p) const {
    assert(x.size() == nx);
    assert(p.size() == nc);
    assert(grad_cx_p.size() == nx);
    impl->grad_c_prod({x.data(), param.data(), p.data()}, {grad_cx_p.data()});
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_gn_hess_constr(index_t, crvec x,
                                                         crvec M,
                                                         rmat out) const {
    auto &&sparse = impl->gn_hess_c.fun.sparsity_out(0);
    assert(x.size() == nx);
    assert(M.size() == nc);
    assert(out.rows() == nx);
    assert(out.cols() == nx);
    assert(work.size() >= static_cast<length_t>(sparse.nnz()));
    impl->gn_hess_c({x.data(), param.data(), M.data()}, {work.data()});
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    if (sparse.is_dense())
        out += cmmat{work.data(), nx, nx};
    else
        out += cmspmat{
            nx,
            nx,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_constr_N(crvec x, rvec c) const {
    if (nc_N == 0)
        return;
    assert(x.size() == nx);
    assert(c.size() == nc_N);
    impl->c_N({x.data(), param.data()}, {c.data()});
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_grad_constr_prod_N(crvec x, crvec p,
                                                         rvec grad_cx_p) const {
    assert(x.size() == nx);
    assert(p.size() == nc_N);
    assert(grad_cx_p.size() == nx);
    impl->grad_c_prod_N({x.data(), param.data(), p.data()}, {grad_cx_p.data()});
}

template <Config Conf>
void CasADiControlProblem<Conf>::eval_add_gn_hess_constr_N(crvec x, crvec M,
                                                           rmat out) const {
    auto &&sparse = impl->gn_hess_c.fun.sparsity_out(0);
    assert(x.size() == nx);
    assert(M.size() == nc_N);
    assert(out.rows() == nx);
    assert(out.cols() == nx);
    assert(work.size() >= static_cast<length_t>(sparse.nnz()));
    impl->gn_hess_c_N({x.data(), param.data(), M.data()}, {work.data()});
    using spmat   = Eigen::SparseMatrix<real_t, Eigen::ColMajor, casadi_int>;
    using cmspmat = Eigen::Map<const spmat>;
    if (sparse.is_dense())
        out += cmmat{work.data(), nx, nx};
    else
        out += cmspmat{
            nx,
            nx,
            static_cast<length_t>(sparse.nnz()),
            sparse.colind(),
            sparse.row(),
            work.data(),
        };
}

END_ALPAQA_CASADI_LOADER_NAMESPACE
} // namespace alpaqa