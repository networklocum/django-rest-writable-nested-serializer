from rest_framework import serializers

class WritableNestedByIdLookup():

    def create(self, validated_data, *args, **kwargs):
        new_m2m_lists = self.create_m2m_lists(validated_data)
        instance = super().create(validated_data, *args, **kwargs)
        self.set_m2m_lists(instance, new_m2m_lists)
        return instance

    def update(self, instance, validated_data, *args, **kwargs):
        new_m2m_lists = self.create_m2m_lists(validated_data)
        instance = super().update(instance, validated_data, *args, **kwargs)
        self.set_m2m_lists(instance, new_m2m_lists)
        return instance

    def create_m2m_lists(self, validated_data):
        assert (
            hasattr(self.Meta, "many_to_many_write_by_id_fields"),
            "many_to_many_write_by_id_fields should be a tuple or a list."
        )
        new_m2m_lists = {}
        for field_name in self.Meta.many_to_many_write_by_id_fields:
            field_data = validated_data.pop(field_name, None)
            if field_data:
                serializer_field = self.get_fields()[field_name]
                FieldModel = serializer_field.child.Meta.model
                field_instances = self.validate_field_instance_members(field_data, field_name, FieldModel)
                new_m2m_lists[field_name] = field_instances
        return new_m2m_lists

    def set_m2m_lists(self, instance, m2m_lists):
        for field_name, field_instances in m2m_lists.items():
            getattr(instance, field_name).set(field_instances)

    def validate_field_instance_members(self, field_data, field_name, FieldModel):
        if type(field_data) is not list:
            raise serializers.ValidationError("{} must be a list".format(field_name))

        try:
            field_instances = [FieldModel.objects.get(pk=x['id']) for x in field_data]
        except  IndexError:
            raise serializers.ValidationError(
                "{} must be a list of dictionaries containing an 'id' field".format(field_name)
            )
        except FieldModel.DoesNotExist as e:
            raise serializers.ValidationError(
                str(e)
            )
        return field_instances
