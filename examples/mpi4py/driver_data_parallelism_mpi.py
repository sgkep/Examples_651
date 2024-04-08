from mpi4py import MPI
import numpy as np

'''
Data parallelism is a common approach in distributed computing, where the data
is divided into chunks and processed by different workers simultaneously. In
the context of linear regression using the mpi4py library (which is a Python
wrapper for the Message Passing Interface), you can perform data parallelism
by distributing different subsets of your dataset to multiple processes for
parallel computation.

Here's an example of how you could implement data parallelism with mpi4py for
linear regression using a basic gradient descent algorithm.

In this example, we've divided the dataset into chunks based on the number of
MPI processes (size). Each process performs a local linear regression
computation using its own subset of the data and updates its own local
gradient. The Allreduce function is used to combine the gradients across all
processes, allowing each process to incorporate information from other
processes before updating the coefficients.

Finally, the coefficients are gathered to the root process (rank 0) and
averaged to obtain the final coefficients of the linear regression model.

Remember that this is a basic example, and in a real-world scenario, you
might need to handle more complexities such as data preprocessing,
regularization, and convergence criteria.

To execute:

> mpirun python -m mpi4py driver_data_parallelism_mpi.py


Code mostly generated by ChatGPT, 2023-08-15. I fixed a few issues.

The computations were not throughly checked.

'''

num_samples = 1000
num_features = 5

# MPI setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Split the data into chunks for parallel processing
chunk_size = num_samples // size
start_idx = rank * chunk_size
end_idx = start_idx + chunk_size

if rank == 0:
    # Simulated dataset
    np.random.seed(0)
    X = np.random.rand(num_samples, num_features)
    y = 2 * X[:, 0] + 3 * X[:, 1] - 1.5 * X[:, 2] + np.random.randn(num_samples)

    X = [ X[(i*chunk_size):((i+1)*chunk_size)] for i in range(size)]
    y = [ y[(i*chunk_size):((i+1)*chunk_size)] for i in range(size)]
else:
    X = None
    y = None

# Scatter data to all processes
local_X = comm.scatter(X, root=0)
local_y = comm.scatter(y, root=0)

# Initialize coefficients and learning rate
num_features = local_X.shape[1]
np.random.seed(0)
theta = np.random.rand(num_features)
learning_rate = 0.01
num_iterations = 1000

# Gradient descent
for iteration in range(num_iterations):
    # Compute predictions and errors
    predictions = np.dot(local_X, theta)
    errors = predictions - local_y

    # Compute gradient for local subset
    gradient = np.dot(local_X.T, errors) / chunk_size

    # Reduce gradients across processes
    comm.Allreduce(MPI.IN_PLACE, gradient, op=MPI.SUM)

    # Update coefficients
    theta -= learning_rate * gradient

# Gather updated coefficients to the root process
all_thetas = comm.gather(theta, root=0)

if rank == 0:
    # Average the coefficients from all processes
    final_theta = np.mean(all_thetas, axis=0)
    print("Final Coefficients:", final_theta)
