import pytest
from sqlalchemy.orm import Session
from app.api.users.model import User
from app.api.communities.model import Community, CommunityMember
# Adicionei PostLikes aqui nos imports
from app.api.post.model import Post, CampaignPost, PostLikes
from app.api.post.schemas import PostTypeEnum, PostStatusEnum
from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.notifications.listeners import register_listeners

# Registra os listeners antes dos testes para garantir que os eventos sejam disparados
register_listeners()

@pytest.fixture
def setup_scenario(session_sql: Session):
    """Fixture que monta o cenário: 1 Admin, 1 Membro, 1 Comunidade."""
    # Admin (Autor)
    admin = User(username="admin_listener", email="admin_listener@test.com", name="Admin Listener", hashed_password="x")
    session_sql.add(admin)
    
    # Membro (Destinatário/Interator)
    member = User(username="member_listener", email="member_listener@test.com", name="Member Listener", hashed_password="x")
    session_sql.add(member)
    session_sql.flush()

    # Comunidade
    community = Community(name="Comunidade Listener", type_community="public")
    session_sql.add(community)
    session_sql.flush()

    # Associação
    mem_admin = CommunityMember(user_id=admin.id, community_id=community.id, role="admin")
    mem_user = CommunityMember(user_id=member.id, community_id=community.id, role="member")
    session_sql.add_all([mem_admin, mem_user])
    session_sql.commit()

    return {"admin": admin, "member": member, "community": community, "mem_user": mem_user}

@pytest.mark.integration
def test_listener_official_announcement(session_sql: Session, setup_scenario):
    """
    Testa se criar um ANNOUNCEMENT gera notificação OFFICIAL_NOTICE para o membro.
    """
    data = setup_scenario
    admin = data['admin']
    member = data['member']
    community = data['community']

    # 1. Criar Anúncio
    post = Post(
        community_id=community.id,
        user_id=admin.id,
        user_role_in_community="admin",
        type_post=PostTypeEnum.ANNOUNCEMENT,
        title="Manutenção Urgente",
        content="O sistema vai reiniciar.",
        status=PostStatusEnum.ACTIVE
    )
    session_sql.add(post)
    session_sql.commit()

    # 2. Verificar se o MEMBRO recebeu a notificação
    notif = session_sql.query(Notification).filter(
        Notification.type == NotificationTypeEnum.OFFICIAL_NOTICE,
    ).all()
    
    my_notif = next((n for n in notif if str(n.user_id) == str(member.id)), None)

    assert my_notif is not None
    assert my_notif.data['notice_title'] == "Manutenção Urgente"

@pytest.mark.integration
def test_listener_campaign_lifecycle(session_sql: Session, setup_scenario):
    """
    Testa o ciclo de vida de uma campanha: Criação -> Aprovação -> Cancelamento.
    Verifica se o AUTOR recebe as notificações de status.
    """
    data = setup_scenario
    admin = data['admin'] # Autor da campanha
    community = data['community']

    # 1. Criar Campanha
    post = Post(
        community_id=community.id, user_id=admin.id, user_role_in_community="admin",
        type_post=PostTypeEnum.CAMPAIGN, title="Minha Campanha Listener", content="...",
        status=PostStatusEnum.ACTIVE
    )
    session_sql.add(post)
    session_sql.flush()

    campaign = CampaignPost(post_id=post.id, status_campaign="pending")
    session_sql.add(campaign)
    session_sql.commit()

    # 2. Atualizar para APROVADA
    campaign.status_campaign = "approved"
    session_sql.add(campaign)
    session_sql.commit() 

    # Verifica notificação de aprovação
    all_notifs = session_sql.query(Notification).filter(
        Notification.type == NotificationTypeEnum.CAMPAIGN
    ).all()
    
    notif_approved = next((n for n in all_notifs 
                           if str(n.user_id) == str(admin.id) 
                           and n.data.get('campaign_status_type') == 'approved'), None)

    assert notif_approved is not None

    # 3. Atualizar para CANCELADA
    campaign.status_campaign = "canceled"
    session_sql.add(campaign)
    session_sql.commit()

    # Verifica notificação de cancelamento
    all_notifs_2 = session_sql.query(Notification).filter(
        Notification.type == NotificationTypeEnum.CAMPAIGN
    ).all()

    notif_canceled = next((n for n in all_notifs_2
                           if str(n.user_id) == str(admin.id) 
                           and n.data.get('campaign_status_type') == 'canceled'), None)

    assert notif_canceled is not None

@pytest.mark.integration
def test_listener_post_like(session_sql: Session, setup_scenario):
    """
    Testa se curtir um post gera notificação de INTERAÇÃO para o dono do post.
    """
    data = setup_scenario
    admin = data['admin']   # Dono do Post
    member = data['member'] # Quem vai curtir
    mem_user = data['mem_user'] # Objeto CommunityMember de quem curte
    community = data['community']

    # 1. Criar Post (pelo Admin)
    post = Post(
        community_id=community.id, 
        user_id=admin.id, 
        user_role_in_community="admin",
        type_post=PostTypeEnum.ANNOUNCEMENT, 
        title="Post Legal", 
        content="...",
        status=PostStatusEnum.ACTIVE
    )
    session_sql.add(post)
    session_sql.commit()

    # 2. Membro curte o Post (Cria registro em PostLikes)
    # O listener deve disparar aqui
    like = PostLikes(post_id=post.id, member_id=mem_user.id)
    session_sql.add(like)
    session_sql.commit()

    # 3. Verificar se o ADMIN (dono do post) recebeu notificação de interação
    notifs = session_sql.query(Notification).filter(
        Notification.type == NotificationTypeEnum.INTERACTION
    ).all()

    # Filtra para achar a notificação específica
    like_notif = next((n for n in notifs 
                       if str(n.user_id) == str(admin.id) 
                       and n.data.get('interaction_type') == 'like'
                       and n.data.get('post_title') == "Post Legal"), None)

    assert like_notif is not None
    assert like_notif.data['actor_name'] == "Member Listener"