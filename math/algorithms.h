#if LADA_MATH_MODULE != 1
  //! \brief Computes the Gruber cell of a lattice.
  //! \details Shamelessly adapted from the computational rystallography
  //!          tool box.
  LADA_INLINE rMatrix3d gruber( rMatrix3d const &_in, 
                                size_t itermax = 0,
                                types::t_real _tol = types::tolerance )
    LADA_END( return ( (rMatrix3d(*)( rMatrix3d const &,
                                      size_t itermax, 
                                      types::t_real ))
                       api_capsule[LADA_SLOT(math)] )
                     (_in, itermax, _tol); )
#else
  api_capsule[LADA_SLOT(math)] = (void *)gruber;
#endif
#define BOOST_PP_VALUE BOOST_PP_INC(LADA_SLOT(math))
#include LADA_ASSIGN_SLOT(math)

#if LADA_MATH_MODULE != 1
  //! \brief Computes the parameters of the metrical matrix associated with
  //!        the gruber cell.
  LADA_INLINE Eigen::Matrix<types::t_real, 6, 1>
    gruber_parameters( rMatrix3d const &_in,
                       size_t itermax = 0,
                       types::t_real _tol = types::tolerance)
    LADA_END( return ( (Eigen::Matrix<types::t_real, 6, 1>(*)( rMatrix3d const &,
                                      size_t itermax, 
                                      types::t_real ))
                       api_capsule[LADA_SLOT(math)] ) 
                     (_in, itermax, _tol); )
#else
  api_capsule[LADA_SLOT(math)] = (void *)gruber_parameters;
#endif
#define BOOST_PP_VALUE BOOST_PP_INC(LADA_SLOT(math))
#include LADA_ASSIGN_SLOT(math)

#if LADA_MATH_MODULE != 1
  //! Computes smith normal form of a matrix \a  _S = \a _L \a _M \a _R.
  LADA_INLINE void smith_normal_form( iMatrix3d& _S, 
                                      iMatrix3d & _L, 
                                      const iMatrix3d& _M, 
                                      iMatrix3d &_R )
    LADA_END( ( (rMatrix3d(*)( iMatrix3d&, 
                                      iMatrix3d&, 
                                      const iMatrix3d&, 
                                 iMatrix3d& ))
                  api_capsule[LADA_SLOT(math)] ) 
                (_S, _L, _M, _R); )
#else
  api_capsule[LADA_SLOT(math)] = (void *)smith_normal_form;
#endif
#define BOOST_PP_VALUE BOOST_PP_INC(LADA_SLOT(math))
#include LADA_ASSIGN_SLOT(math)
