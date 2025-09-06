from aiida.orm import AtomicOrbitalData

node = AtomicOrbitalData.get_or_create(
    source="Si.upf",
    source_orbital="Si_gga_10au_100Ry_3s3p2d.orb"
)
