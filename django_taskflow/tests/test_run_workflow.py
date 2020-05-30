import pytest

@pytest.mark.django_db
def test_simple_workflow(django_user_model):

    user = django_user_model.objects.create(username="test user",
                                            password='tupass')
    context = {'user': user,
               }


    
