#ifndef LADA_LNS_XPR_PUSHBACK_H
#define LADA_LNS_XPR_PUSHBACK_H

#include "LaDaConfig.h"

#include "utilities.h"
#include "../action/shared_ptr.h"

namespace LaDa 
{
  namespace load_n_save
  {
    namespace xpr
    {
      namespace details
      {
        //! Saves or loops containers with begin/end, and pushback method.
        template<class T>
          struct PushBack
          {
            PushBack(T &_container) : container_(_container) {}
            PushBack(PushBack<T> const &_c) : container_(_c.container_) {}
            template<class T_ARCHIVE>
              bool lns_access(T_ARCHIVE &_ar, const unsigned int)
              {
                if(_ar.is_loading())
                {
                  typename T::value_type value;
                  while(_ar & ext(value)) container_.push_back(value);
                  return true;
                }
                else 
                {
                  bool is_good = true;
                  typename T::iterator i_first = container_.begin();
                  typename T::iterator i_end = container_.end();
                  for(; i_first != i_end; ++i_first) is_good &= _ar & ext(*i_first);  
                  return is_good;
                }
              }
            T &container_;
          };
        //! Saves or loops containers with begin/end, and pushback method.
        template<class T>
          struct PushBack<T const>
          {
            PushBack(T const &_container) : container_(_container) {}
            PushBack(PushBack<T> const &_c) : container_(_c.container_) {}
            template<class T_ARCHIVE>
              bool lns_access(T_ARCHIVE &_ar, const unsigned int)
              {
                LADA_ASSERT(not _ar.is_loading(), "Cannot load into constant container.")
                typename  T::value_type value;
                while(_ar & ext(value)) container_.push_back(value);
                return true;
              }
            T const &container_;
          };
      } // namespace details

    } // namespace xpr
    template<class T>
      xpr::Section push_back(T const &_container)
      { return ext(copy(xpr::details::PushBack<T const>(_container))); }
    template<class T> xpr::Section push_back(T &_container)
    {
      xpr::details::PushBack<T> data(_container);
      return ext(copy(data)); 
    }
  } // namespace load_n_save
} // namespace LaDa
#endif