import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
from copy import deepcopy
import torch
from typing import Any
import time as time
from tqdm import tqdm
from ase import Atoms
from dataclasses import dataclass
import json

from popcornn.paths import get_path
from popcornn.optimization import initialize_path
from popcornn.optimization import PathOptimizer
from popcornn.tools import process_images, output_to_atoms
from popcornn.tools import ODEintegrator
from popcornn.potentials import get_potential


class Popcornn:
    """
    Wrapper class for Popcornn optimization.
    """
    def __init__(
            self, 
            images: list[Atoms],
            unwrap_positions: bool = True,
            path_params: dict[str, Any] = {},
            num_record_points: int = 101,
            output_dir: str | None = None,
            device: str | None = None,
            dtype: str = "float32",
            seed: int | None = 0,
    ):
        """
        Initialize the Popcornn class.

        Args:
            images (list[Atoms]): List of ASE Atoms objects representing the images.
            unwrap_positions (bool): Whether to unwrap the positions of the images. Default is True.
            path_params (dict[str, Any]): Parameters for the path prediction method.
            num_record_points (int): Number of points to record along the path when returning and saving the optimized path.
            output_dir (str | None): Directory to save the output files. If None, no files will be saved.
            device (str | None): Device to use for optimization. If None, will use 'cuda' if available, otherwise 'cpu'.
            dtype (str): Data type to use for optimization. Can be 'float32' or 'float64'.
            seed (int | None): Random seed for reproducibility. If None, no seed is set.
        """
        # Set device
        if device is None:
            device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        if isinstance(device, str):
            device = torch.device(device)
        if device.type == 'cuda':
            torch.cuda.empty_cache()
        self.device = device

        # Set dtype
        if dtype == "float32":
            self.dtype = torch.float32
        elif dtype == "float64":
            self.dtype = torch.float64
        else:
            raise ValueError(f"Invalid dtype: {dtype}. Use 'float32' or 'float64'.")

        # Set random seed
        if seed is not None:
            torch.manual_seed(seed)

        # Process images
        self.images = process_images(images, unwrap_positions=unwrap_positions, device=self.device, dtype=self.dtype)

        # Get path prediction method
        self.path = get_path(images=self.images, **path_params, device=self.device, dtype=self.dtype)

        # Randomly initialize the path, otherwise a straight line
        if len(images) > 2:
            self.path = initialize_path(
                path=self.path, 
                times=torch.linspace(self.path.t_init.item(), self.path.t_final.item(), len(self.images), device=self.device), 
                init_points=self.images.positions,
            )

        # Create output directories
        self.output_dir = output_dir
        if self.output_dir is not None:
            os.makedirs(self.output_dir, exist_ok=True)
        self.num_record_points = num_record_points

    
    def optimize_path(
            self,
            *optimization_params: list[dict],
            output_ase_atoms: bool = True
    ):
        """
        Run the optimization.
        
        Args:
            optimization_params (list[dict]): 
                List of dictionaries containing the parameters for each optimization run.
                Each dictionary should contain the following keys:
                - potential_params: Parameters for the potential.
                - integrator_params: Parameters for the loss integrator.
                - optimizer_params: Parameters for the path optimizer.
                - num_optimizer_iterations: Number of optimization iterations.
            num_record_points (int): 
                Number of points to record along the path when returning and saving the optimized path.
        """
        # Optimize the path
        for i, params in enumerate(optimization_params):
            if self.output_dir is not None:
                output_dir = f"{self.output_dir}/opt_{i}"
            else:
                output_dir = None

            self._optimize(
                **params, 
                output_dir=output_dir,
                output_ase_atoms=output_ase_atoms
            )

        # Evaluate points along the optimized path and return
        time = torch.linspace(self.path.t_init.item(), self.path.t_final.item(), self.num_record_points, device=self.device)
        ts_time = torch.tensor([self.path.ts_time], device=self.device, dtype=self.dtype)
        path_output = self.path(time, return_velocities=True, return_energies=True, return_forces=True)
        ts_output = self.path(ts_time, return_velocities=True, return_energies=True, return_forces=True)
        if issubclass(self.images.image_type, Atoms) and output_ase_atoms:
            images, ts_images = output_to_atoms(path_output, self.images), output_to_atoms(ts_output, self.images)
            return images, ts_images[0]
        else:
            return path_output, ts_output

    def _optimize(
            self,
            potential_params: dict[str, Any] = {},
            integrator_params: dict[str, Any] = {},
            optimizer_params: dict[str, Any] = {},
            num_optimizer_iterations: int = 1000,
            output_dir: str | None = None,
            output_ase_atoms: bool = True
    ):
        """
        Optimize the minimum energy path.
        """
        # Create output directories
        if output_dir is not None:
            os.makedirs(output_dir, exist_ok=True)

        # Get potential energy function
        potential = get_potential(images=self.images, **potential_params, device=self.device, dtype=self.dtype)
        self.path.set_potential(potential)

        # Path optimization tools
        integrator = ODEintegrator(**integrator_params, device=self.device, dtype=self.dtype)

        # Gradient descent path optimizer
        optimizer = PathOptimizer(path=self.path, **optimizer_params, device=self.device, dtype=self.dtype)

        # Create output directories
        if output_dir is not None:
            os.makedirs(output_dir, exist_ok=True)
            log_dir = os.path.join(output_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
        
        # Optimize the path
        for optim_idx in tqdm(range(num_optimizer_iterations)):
            try:
                path_integral = optimizer.optimization_step(self.path, integrator)
            except ValueError as e:
                print("ValueError", e)
                raise e

            # Save the path
            if output_dir is not None:
                time = path_integral.t.flatten()
                ts_time = torch.tensor([self.path.ts_time], device=self.device, dtype=self.dtype)
                path_output = self.path(time, return_velocities=True, return_energies=True, return_forces=True)
                ts_output = self.path(ts_time, return_velocities=True, return_energies=True, return_forces=True)
                
                with open(os.path.join(log_dir, f"output_{optim_idx}.json"), 'w') as file:
                    json.dump(
                        {
                            "time": time.tolist(),
                            "positions": path_output.positions.tolist(),
                            "energies": path_output.energies.tolist(),
                            "velocities": path_output.velocities.tolist(),
                            "forces": path_output.forces.tolist(),
                            "loss_evals": path_integral.y.tolist(),
                            "integral": path_integral.integral.item(),
                            "ts_time": ts_time.tolist(),
                            "ts_positions": ts_output.positions.tolist(),
                            "ts_energies": ts_output.energies.tolist(),
                            "ts_velocities": ts_output.velocities.tolist(),
                            "ts_forces": ts_output.forces.tolist(),
                        }, 
                        file,
                    )

            # Check for convergence
            if optimizer.converged:
                print(f"Converged at step {optim_idx}")
                break
            
        

