import torch
from torch import nn
from dataclasses import dataclass

@dataclass
class PotentialOutput():
    """
    Data class representing the output of a path computation.

    Attributes:
    -----------
    energies : torch.Tensor
        The potential energies of the path.
    forces : torch.Tensor, optional
        The forces along the path.
    """
    energies: torch.Tensor = None
    forces: torch.Tensor = None
    energies_decomposed: torch.Tensor = None
    forces_decomposed: torch.Tensor = None



class BasePotential(nn.Module):
    def __init__(self, images, device, dtype, add_azimuthal_dof=False, add_translation_dof=False, **kwargs) -> None:
        super().__init__()
        self.atomic_numbers = images.atomic_numbers if images.atomic_numbers is not None else None
        self.n_atoms = len(images.atomic_numbers) if images.atomic_numbers is not None else None
        self.pbc = images.pbc if images.pbc is not None else None
        self.cell = images.cell if images.cell is not None else None
        self.tags = images.tags if images.tags is not None else None
        self.charge = images.charge if images.charge is not None else None
        self.spin = images.spin if images.spin is not None else None
        self.point_option = 0  # TODO: remove this
        self.point_arg = 0  # TODO: remove this
        if add_azimuthal_dof:  # TODO: remove this
            self.point_option = 1  # TODO: remove this
            self.point_arg = add_azimuthal_dof  # TODO: remove this
        elif add_translation_dof:  # TODO: remove this
            self.point_option = 2  # TODO: remove this
        self.device = device
        self.dtype = dtype
        
        # Put model in eval mode
        self.eval()

    @staticmethod 
    def calculate_conservative_forces(energies, position, create_graph=True):
        return -torch.autograd.grad(
            energies,
            position,
            grad_outputs=torch.ones_like(energies),
            create_graph=create_graph,
        )[0]
    
    @staticmethod
    def calculate_conservative_forces_decomposed(energies_decomposed, position, create_graph=True):
        _forceterm_fxn = torch.vmap(
            lambda vec: -torch.autograd.grad(
                energies_decomposed.flatten(), 
                position,
                grad_outputs=vec,
                create_graph=create_graph,
            )[0],
        )
        inp_vec = torch.eye(
            energies_decomposed.shape[1], device=energies_decomposed.device
        ).repeat(1, energies_decomposed.shape[0])
        return _forceterm_fxn(inp_vec).transpose(0, 1)

    def forward(
            self,
            positions: torch.Tensor
    ) -> PotentialOutput:
        raise NotImplementedError
