from rest_framework.metadata import SimpleMetadata


class JoinBudgetMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)
        metadata['actions'] = {
            'POST': {
                'id': {
                    'type': 'UUID',
                    'required': True,
                    'read_only': False,
                }
            }
        }
        return metadata
