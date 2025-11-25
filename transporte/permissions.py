from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado:
    - Métodos seguros (GET, HEAD, OPTIONS): cualquiera
    - Métodos de escritura (POST, PUT, PATCH, DELETE): solo administradores autenticados
    """
    
    def has_permission(self, request, view):
        # Los métodos seguros están permitidos para cualquiera
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Los métodos de escritura requieren autenticación Y ser admin (staff)
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado:
    - Solo el propietario del objeto o un administrador puede editarlo/eliminarlo
    """
    
    def has_object_permission(self, request, view, obj):
        # Los métodos seguros están permitidos para cualquiera
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar si es admin
        if request.user.is_staff:
            return True
        
        # Verificar si es el propietario (si el objeto tiene user)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
