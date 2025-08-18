from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from core.models.Licensed import Licensed
from .models import UnilevelNetwork


class DirectsTreeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Identifica se é administrador (superuser, staff ou grupo "Administrador")
        is_admin = (
            getattr(request.user, 'is_superuser', False)
            or getattr(request.user, 'is_staff', False)
            or request.user.groups.filter(name='Administrador').exists()
        )

        # Serializador de nó
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

        if is_admin:
            # Carrega todas as relações diretas (level=1) de toda a rede
            relations = (
                UnilevelNetwork.objects
                .filter(level=1)
                .select_related('upline_licensed__user', 'downline_licensed__user')
            )

            # Mapa de adjacência: upline_id -> [Licensed filhos]
            adjacency = {}
            all_licensed_by_id = {}
            upline_ids = set()
            downline_ids = set()
            for rel in relations:
                upline_ids.add(rel.upline_licensed_id)
                downline_ids.add(rel.downline_licensed_id)
                all_licensed_by_id[rel.upline_licensed_id] = rel.upline_licensed
                all_licensed_by_id[rel.downline_licensed_id] = rel.downline_licensed
                adjacency.setdefault(rel.upline_licensed_id, []).append(rel.downline_licensed)

            # Determina raízes
            roots_qs = Licensed.objects.filter(is_root=True).select_related('user')
            root_ids_is_root = {lic.id for lic in roots_qs}
            computed_root_ids = (upline_ids - downline_ids) if upline_ids else set()
            all_root_ids = (root_ids_is_root | computed_root_ids)

            # Inclui Licensed isolados marcados como raiz (sem arestas)
            for lic in roots_qs:
                all_licensed_by_id.setdefault(lic.id, lic)
                adjacency.setdefault(lic.id, [])

            # Se não houver nenhuma raiz detectada, retorna vazio
            if not all_root_ids:
                return Response({'root': None})

            # Constrói nós
            id_to_node = {}

            def build_subtree(start_lic: Licensed):
                # BFS para montar todos os níveis a partir de um root
                id_to_node[start_lic.id] = serialize_node(start_lic, 0)
                queue = [(start_lic, 0)]
                while queue:
                    parent_lic, parent_level = queue.pop(0)
                    parent_node = id_to_node[parent_lic.id]
                    for child_lic in adjacency.get(parent_lic.id, []):
                        if child_lic.id not in id_to_node:
                            id_to_node[child_lic.id] = serialize_node(child_lic, parent_level + 1)
                        parent_node['children'].append(id_to_node[child_lic.id])
                        queue.append((child_lic, parent_level + 1))

            forest_nodes = []
            for rid in all_root_ids:
                lic_root = all_licensed_by_id.get(rid)
                if not lic_root:
                    # Assegura carregar caso não tenha vindo via relations
                    try:
                        lic_root = Licensed.objects.select_related('user').get(id=rid)
                    except Licensed.DoesNotExist:
                        continue
                build_subtree(lic_root)
                forest_nodes.append(id_to_node[lic_root.id])

            # Se houver apenas uma raiz, retorna diretamente sem nó agregador
            def count_directs(n):
                n['directs'] = len(n['children'])
                for c in n['children']:
                    count_directs(c)

            if len(forest_nodes) == 1:
                single_root = forest_nodes[0]
                count_directs(single_root)
                return Response({'root': single_root})

            # Caso existam múltiplas raízes, usa nó agregador para manter compatibilidade
            aggregator_root = {
                'id': 0,
                'level': 0,
                'user': {
                    'username': 'Rede',
                    'image_profile': None,
                },
                'children': forest_nodes,
            }
            count_directs(aggregator_root)
            return Response({'root': aggregator_root})

        # Usuário comum: encontra seu Licensed e retorna todos os níveis (sem limite de 5)
        try:
            root_licensed = Licensed.objects.select_related('user').get(user=request.user)
        except Licensed.DoesNotExist:
            return Response({'root': None})

        # Busca progressiva até esgotar os níveis usando apenas relações diretas (level=1)
        level_to_nodes = {0: [root_licensed]}
        edges = []
        current_level = [root_licensed]
        level_index = 1
        while current_level:
            next_level = []
            rels = (
                UnilevelNetwork.objects
                .filter(upline_licensed__in=current_level, level=1)
                .select_related('upline_licensed__user', 'downline_licensed__user')
            )
            for r in rels:
                edges.append((r.upline_licensed_id, r.downline_licensed_id, level_index))
                next_level.append(r.downline_licensed)
            if not next_level:
                break
            level_to_nodes[level_index] = next_level
            current_level = next_level
            level_index += 1

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

        def count_directs(n):
            n['directs'] = len(n['children'])
            for c in n['children']:
                count_directs(c)
        count_directs(root)

        return Response({'root': root})


