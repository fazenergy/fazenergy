from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models.Licensed import Licensed
from .models import UnilevelNetwork


class DirectsTreeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            root_licensed = Licensed.objects.select_related('user').get(user=request.user)
        except Licensed.DoesNotExist:
            return Response({"root": None})

        # Precarrega todas as relações de até 5 níveis abaixo do root
        # Busca progressiva até 5 níveis usando apenas relações diretas (level=1)
        level_to_nodes = {0: [root_licensed]}
        all_nodes = {root_licensed.id: root_licensed}
        edges = []

        current_level = [root_licensed]
        for lvl in range(1, 6):
            next_level = []
            rels = (
                UnilevelNetwork.objects
                .filter(upline_licensed__in=current_level, level=1)
                .select_related('upline_licensed__user', 'downline_licensed__user')
            )
            for r in rels:
                edges.append((r.upline_licensed_id, r.downline_licensed_id, lvl))
                all_nodes.setdefault(r.downline_licensed_id, r.downline_licensed)
                next_level.append(r.downline_licensed)
            if not next_level:
                break
            level_to_nodes[lvl] = next_level
            current_level = next_level

        # Monta estrutura em árvore
        def serialize_node(lic: Licensed, level: int):
            return {
                'id': lic.id,
                'level': level,
                'user': {
                    'username': lic.user.username,
                    'image_profile': getattr(lic.user, 'image_profile', None) and lic.user.image_profile.url if getattr(lic.user, 'image_profile', None) else None,
                },
                'children': []
            }

        id_to_node = {root_licensed.id: serialize_node(root_licensed, 0)}
        for lvl, nodes in level_to_nodes.items():
            if lvl == 0:
                continue
            for lic in nodes:
                id_to_node[lic.id] = serialize_node(lic, lvl)

        for up_id, down_id, lvl in edges:
            parent = id_to_node.get(up_id)
            child = id_to_node.get(down_id)
            if parent and child:
                parent['children'].append(child)

        root = id_to_node[root_licensed.id]
        # Calcula diretos
        def count_directs(n):
            n['directs'] = len(n['children'])
            for c in n['children']:
                count_directs(c)
        count_directs(root)

        return Response({'root': root})


