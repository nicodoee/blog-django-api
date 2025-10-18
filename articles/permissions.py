from rest_framework import permissions

class CanCreateArticle(permissions.BasePermission):
  """
  Seuls admin, moderator et author peuvent créer des articles
  """
  def has_permission(self, request, view):
    if request.method == 'POST':
      try:
        user_role = request.user.role.role
        return user_role in ['admin', 'moderator', 'author']
      except:
        return False
    return True


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
  """
  L'auteur peut modifier son propre article
  Admin et Moderator peuvent modifier tous les articles
  """
  def has_object_permission(self, request, view, obj):
    # Read permissions
    if request.method in permissions.SAFE_METHODS:
      return True

    # Write permissionszz
    try:
      user_role = request.user.role.role

      # Admin et Moderator peuvent tout modifier
      if user_role in ['admin', 'moderator']:
        return True

      # L'auteur peut modifier son propre article
      if user_role == 'author' and obj.author == request.user:
        return True

      return False
    except:
      return False


class CanPublishArticle(permissions.BasePermission):
  """
  Seuls admin et moderator peuvent publier des articles
  """
  def has_permission(self, request, view):
    try:
      user_role = request.user.role.role
      return user_role in ['admin', 'moderator']
    except:
      return False


class CanDeleteArticle(permissions.BasePermission):
  """
  Admin et Moderator peuvent supprimer tous les articles
  L'auteur peut supprimer son propre article
  """
  def has_object_permission(self, request, view, obj):
    try:
      user_role = request.user.role.role

      # Admin et Moderator peuvent tout supprimer
      if user_role in ['admin', 'moderator']:
        return True

      # L'auteur peut supprimer son propre article
      if user_role == 'author' and obj.author == request.user:
        return True

      return False
    except:
      return False


class CanViewArticle(permissions.BasePermission):
  """
  Gère la visibilité des articles selon leur statut
  """
  def has_object_permission(self, request, view, obj):
    # Articles supprimés : seulement admin/moderator
    if obj.is_deleted:
      try:
        user_role = request.user.role.role
        return user_role in ['admin', 'moderator']
      except:
          return False

    # Articles publiés : tout le monde
    if obj.status == 'published':
      return True

    # Articles draft/pending : auteur, admin, moderator
    try:
      user_role = request.user.role.role
      if user_role in ['admin', 'moderator']:
        return True
      if obj.author == request.user:
          return True
    except:
        pass

    return False