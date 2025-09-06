from lazy_loader import attach

__getattr__, __dir__, __all__ = attach(
    __name__,
    submodules=[
        "utils",
        "audio_split",
        "checkGPU",
        "message",
    ],
    submod_attrs={
        "utils": ["EPS"],
    },
)

