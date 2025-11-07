# Este archivo hace que la carpeta ui sea un paquete Python
from .login_frame import LoginFrame
from .cliente_frame import ClienteFrame
from .admin_frame import AdminFrame
from .perfil_frame import PerfilFrame

__all__ = ['LoginFrame', 'ClienteFrame', 'AdminFrame', 'PerfilFrame']