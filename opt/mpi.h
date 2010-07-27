#ifndef _LADA_MPI_OBJECT_H_
#define _LADA_MPI_OBJECT_H_

#include "LaDaConfig.h"

#ifdef LADA_MPI
# include <boost/mpi/communicator.hpp>
# include <boost/serialization/complex.hpp>
# include <boost/type_traits/add_reference.hpp>
# include <complex>

# include "debug.h"


  namespace LaDa
  {
    namespace mpi
    {
      //! Adds a communicator pointer to a class.
      class AddCommunicator
      {
        public:
          //! Constructor.
          AddCommunicator() : comm_(NULL) {} 
          //! Constructor.
          AddCommunicator( boost::mpi::communicator &_c ) : comm_( &_c ) {} 
          //! Copy Constructor.
          AddCommunicator( const AddCommunicator &_c ) : comm_( _c.comm_ ) {} 

          //! Sets mpi pointer.
          void set_mpi( boost::mpi::communicator* _c )
          {
            LADA_NASSERT( _c == NULL, "Pointer not set.\n" )
            comm_ = _c;
          }
          
          //! Returns reference to communicator.
          boost::mpi::communicator &comm()
          {
            LADA_NASSERT( comm_ == NULL, "Pointer not set.\n" )
            return *comm_;
          }
          //! Returns a constant reference to communicator.
          const boost::mpi::communicator &comm() const 
          {
            LADA_NASSERT( comm_ == NULL, "Pointer not set.\n" )
            return *comm_;
          }

        protected:

          //! The MPI Communicator.
          boost::mpi::communicator *comm_;
      };

      //! A class to easily create and pass two object to mpi.
      template< class FIRST, class SECOND >
      struct Pair
      {
        //! A reference type to the first type.
        typedef typename boost::add_reference<FIRST> :: type t_First;
        //! A reference type to the second type.
        typedef typename boost::add_reference<SECOND> :: type t_Second;
        //! The first reference.
        t_First first;
        //! The second reference.
        t_Second second;
        //! The constructor and initializer.
        Pair( t_First _first, t_Second _second ) : first( _first ), second( _second ) {}
        //! The copy constructor.
        Pair( const Pair &_c ) : first( _c.first ), second( _c.second ) {}
        //! The serialize member.
        template<class ARCHIVE> void serialize(ARCHIVE & _ar, const unsigned int _version)
          { _ar & first; _ar & second; }
      };
    }
  }

# define MPI_COMMDEC ::LaDa::mpi::AddCommunicator
# define MPI_COMMA ,
# define MPI_COMMCOPY( _c ) ::LaDa::mpi::AddCommunicator( _c )
# define MPI_COMM ::LaDa::mpi::AddCommunicator::comm()

# define LADA_MPI_CODE(code) code
# define LADA_ROOT(__comm, code) if( __comm.rank() == 0 ) { code } 
# define LADA_MPI_START \
       boost::scoped_ptr< boost::mpi::environment > env; \
       boost::scoped_ptr< boost::mpi::communicator > world; \
       try \
       { \
         env.reset( new boost::mpi::environment (argc, argv) ); \
         world.reset( new boost::mpi::communicator ); \
       } \
       catch ( std::exception &_e ) \
       { \
         std::cerr << "Error encountered while creating MPI environment.\n"; \
         return 0; \
       } \

  // This macro declares iterators which split a loop over mpi processes.
# define LADA_MPI_SPLIT_LOOP( iterator_type, name, container, comm ) \
           const size_t name ## natoms( container.size() ); \
           const size_t name ## mpisize( comm.size() ); \
           const size_t name ## mpirank( comm.rank() ); \
           const size_t name ## nperproc( name ## natoms / name ## mpisize ); \
           const size_t name ## remainder( name ## natoms % name ## mpisize ); \
           const size_t name ## begin_index \
             (   \
                 name ## mpirank * name ## nperproc \
               + std::min( (types::t_int) name ## remainder, (types::t_int) comm.rank() ) \
             ); \
           const size_t name ## end_index \
             (  \
               ( name ## remainder and name ## mpirank < name ## remainder ) ? \
                   name ## nperproc + 1: name ## nperproc  \
             ); \
           iterator_type i_ ## name( container.begin() + name ## begin_index ); \
           const iterator_type i_ ## name ## _end( i_ ## name + name ## end_index );
#else

#  define MPI_COMMDEC
#  define MPI_COMMA
#  define MPI_COMMCOPY( _c ) 
#  define MPI_GETCOMM
#  define MPI_FORWARD_MEMBERS( base ) 
#  define LADA_MPI_SPLIT_LOOP( iterator_type, name, container, comm ) \
            iterator_type i_ ## name( container.begin() ); \
            const iterator_type i_ ## name ## _end( container.end() );
#  define LADA_MPI_CODE(code) 
#  define LADA_ROOT(comm, code) code
#  define LADA_MPI_START
#endif

#endif