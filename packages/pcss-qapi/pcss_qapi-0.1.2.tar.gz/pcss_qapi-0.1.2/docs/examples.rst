Examples
========

PTLayer inference
------------------

::

    import torch

    from pcss_qapi import AuthorizationService
    from pcss_qapi.orca import OrcaProvider

    AuthorizationService.login()

    provider = OrcaProvider()

    backend = provider.get_backend("ORCA-PT-1-A")
    ptlayer = backend.get_ptlayer(in_features=2)
    output = ptlayer(torch.tensor([[1.0,-1.0]],dtype=torch.float32))
