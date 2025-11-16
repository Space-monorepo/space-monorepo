import app.core.init_db

from app.core.database import get_db
from app.api.communities.model import Community, CommunityMember
from app.api.users.model import User
from app.api.users.service import UserService
from app.api.users.schema import UserCreate
from app.core.transaction import TransactionManager


def init_community():

    db = next(get_db())
    from app.api.post.service import PostService
    from app.api.post.schemas import PostCreate, PostTypeEnum
    from app.api.comment.service import CommentService
    from app.api.comment.schema import CommentCreate
    import uuid

    try:
        with TransactionManager(db) as tm:
            user = UserCreate(
                username='space',
                name='Space',
                email='space@space.com',
                hashed_password='spacepassword123',
            )
            user = UserService(tm).create_user(user)
            print(f"User {user.name} created successfully")
            print(f"User email: {user.email} | User ID: {user.id}")

            community = Community(
                name='Space',
                description='Space is a community for space enthusiasts.',
                type_community='company',
            )
            db.add(community)
            db.commit()
            db.refresh(community)
            print(f'Community {community.name} created successfully')


            # Criação do membro admin (criador)
            community_member = CommunityMember(
                user_id=user.id,
                community_id=community.id,
                role='admin',
            )
            db.add(community_member)
            db.commit()
            db.refresh(community_member)
            print(f"Community {community.name} member {user.name} (admin) created successfully")
            admin_member_id = community_member.id

            # listas para armazenar os ids de CommunityMember dos demais membros
            membros_member_ids = []
            moderadores_member_ids = []

            # Criar membros comuns
            membros_info = [
                {"username": "joao", "name": "João Membro", "email": "joao@space.com", "role": "member"},
                {"username": "maria", "name": "Maria Membro", "email": "maria@space.com", "role": "member"},
            ]
            membros = []
            for membro in membros_info:
                membro_user = UserCreate(
                    username=membro["username"],
                    name=membro["name"],
                    email=membro["email"],
                    hashed_password="memberpassword123",
                )
                membro_user = UserService(tm).create_user(membro_user)
                membros.append(membro_user)
                community_member = CommunityMember(
                    user_id=membro_user.id,
                    community_id=community.id,
                    role=membro["role"],
                )
                db.add(community_member)
                db.commit()
                db.refresh(community_member)
                # salvar o id do CommunityMember para uso em comentários
                membros_member_ids.append(community_member.id)
                print(f"Community {community.name} member {membro_user.name} ({membro['role']}) created successfully")

            # Criar moderadores
            moderadores_info = [
                {"username": "carlos", "name": "Carlos Moderador", "email": "carlos@space.com", "role": "moderator"},
                {"username": "ana", "name": "Ana Moderadora", "email": "ana@space.com", "role": "moderator"},
            ]
            moderadores = []
            for mod in moderadores_info:
                mod_user = UserCreate(
                    username=mod["username"],
                    name=mod["name"],
                    email=mod["email"],
                    hashed_password="moderatorpassword123",
                )
                mod_user = UserService(tm).create_user(mod_user)
                moderadores.append(mod_user)
                community_member = CommunityMember(
                    user_id=mod_user.id,
                    community_id=community.id,
                    role=mod["role"],
                )
                db.add(community_member)
                db.commit()
                db.refresh(community_member)
                # salvar o id do CommunityMember para uso em comentários
                moderadores_member_ids.append(community_member.id)
                print(f"Community {community.name} member {mod_user.name} ({mod['role']}) created successfully")

            # Criar alguns pedidos de conexão entre usuários (requests)
            try:
                user_service = UserService(tm)

                # Cada membro pede conexão com o admin
                for membro_user in membros:
                    try:
                        conn = user_service.request_connection(membro_user.id, user.id)
                        print(f"Connection request created: {membro_user.name} -> {user.name} (ID: {conn.id})")
                    except Exception as e:
                        print(f"Could not create connection {membro_user.name} -> {user.name}: {e}")

                # Primeiro membro pede conexão ao segundo membro (se existirem ao menos 2)
                if len(membros) >= 2:
                    try:
                        conn = user_service.request_connection(membros[0].id, membros[1].id)
                        print(f"Connection request created: {membros[0].name} -> {membros[1].name} (ID: {conn.id})")
                    except Exception as e:
                        print(f"Could not create connection {membros[0].name} -> {membros[1].name}: {e}")

                # Um moderador pede conexão ao admin
                if len(moderadores) >= 1:
                    try:
                        conn = user_service.request_connection(moderadores[0].id, user.id)
                        print(f"Connection request created: {moderadores[0].name} -> {user.name} (ID: {conn.id})")
                    except Exception as e:
                        print(f"Could not create connection {moderadores[0].name} -> {user.name}: {e}")

            except Exception as e:
                print(f"Erro ao criar pedidos de conexão: {e}")

            post_service = PostService(tm)
            comment_service = CommentService(tm)
            posts = []

            # Cada membro comum faz um post na comunidade
            for membro_user in membros:
                post_data = PostCreate(
                    community_id=str(community.id),
                    user_id=str(membro_user.id),
                    type_post=PostTypeEnum.ANNOUNCEMENT,
                    title=f"Apresentação de {membro_user.name}",
                    content=f"Olá, sou {membro_user.name} e estou animado para participar da comunidade!",
                    image_url=None,
                )
                post = post_service.create_post(post_data)
                print(f"Post de apresentação criado por {membro_user.name}: '{post.title}' (ID: {post.id})")

            # Cada moderador faz um post na comunidade
            for mod_user in moderadores:
                post_data = PostCreate(
                    community_id=str(community.id),
                    user_id=str(mod_user.id),
                    type_post=PostTypeEnum.ANNOUNCEMENT,
                    title=f"Boas-vindas do moderador {mod_user.name}",
                    content=f"Olá, sou {mod_user.name}, moderador da comunidade. Contem comigo para ajudar no que precisarem!",
                    image_url=None,
                )
                post = post_service.create_post(post_data)
                print(f"Post de boas-vindas criado por {mod_user.name}: '{post.title}' (ID: {post.id})")
            # Campanhas
            campanhas_textos = [
                "Participe da campanha para levar ciência às escolas públicas! Cada doação faz diferença na vida de crianças e jovens. Juntos, podemos transformar o futuro e inspirar novas gerações! Com o seu apoio, poderemos adquirir materiais didáticos, promover palestras e oficinas, além de incentivar o interesse pela ciência desde cedo. Não deixe de contribuir e compartilhar essa ideia com amigos e familiares. A educação é a base para um mundo melhor e mais justo. Venha fazer parte dessa transformação e ajude-nos a alcançar cada vez mais escolas e estudantes! Sua participação é fundamental para o sucesso dessa iniciativa. Doe, divulgue e faça a diferença!",
                "Junte-se à campanha para plantar 100 árvores em nossa cidade e ajude a criar um ambiente mais saudável para todos! O futuro agradece cada semente plantada! Vamos juntos combater as mudanças climáticas, melhorar a qualidade do ar e proporcionar mais áreas verdes para lazer e convivência. Cada árvore representa um passo em direção a um planeta mais sustentável e equilibrado. Participe dessa ação, convide seus amigos, familiares e vizinhos. Doe mudas, ajude no plantio e acompanhe o crescimento das árvores que vão transformar nossa cidade. Sua atitude faz toda a diferença!"
            ]
            for i, texto in enumerate(campanhas_textos):
                post_data = PostCreate(
                    community_id=str(community.id),
                    user_id=str(user.id),
                    type_post=PostTypeEnum.CAMPAIGN,
                    title=f"Campanha {i+1}",
                    content=texto,
                    image_url=None,
                )
                campaign = post_service.create_campaign(post_data)
                post = campaign.post
                print(f"Campanha '{post.title}' criada com sucesso! ID: {post.id}")
                post_service.participate_campaign(post.id, admin_member_id)
                print(f"Usuário {user.id} (CommunityMember {admin_member_id}) inscrito na campanha {post.id}")
                posts.append(post)

            # Denúncias
            denuncias_textos = [
                "Encontrei lixo acumulado próximo ao parque central, incluindo sacolas plásticas, garrafas e outros resíduos que estão prejudicando o ambiente e a saúde dos frequentadores. Solicito providências urgentes da prefeitura para limpeza do local, instalação de lixeiras e campanhas de conscientização da população sobre a importância de manter o espaço limpo. A situação está se agravando a cada dia, trazendo riscos de proliferação de doenças e afastando famílias e crianças do parque. Conto com o apoio das autoridades e da comunidade para resolver esse problema e devolver o parque à população.",
                "Barulho excessivo durante a madrugada na rua das Palmeiras, causado por festas, som alto e aglomerações, tem tirado o sossego dos moradores e dificultado o descanso noturno. Peço fiscalização das autoridades para garantir o cumprimento das leis de silêncio e respeito à vizinhança. A situação tem se repetido frequentemente, prejudicando idosos, crianças e trabalhadores que precisam descansar. Solicito também campanhas educativas para conscientizar sobre a importância do respeito mútuo e da boa convivência."
            ]
            for i, texto in enumerate(denuncias_textos):
                post_data = PostCreate(
                    community_id=str(community.id),
                    user_id=str(user.id),
                    type_post=PostTypeEnum.COMPLAINT,
                    title=f"Denúncia {i+1}",
                    content=texto,
                    image_url=None,
                )
                complaint_response = post_service.create_complaint(post_data)
                post = complaint_response.post
                print(f"Denúncia '{post.title}' criada com sucesso! ID: {post.id}")
                posts.append(post)

            # Enquetes
            enquetes = [
                {
                    "title": "Enquete 1",
                    "question": "Qual tema você gostaria de ver no próximo evento da comunidade?",
                    "content": "Sugira palestrantes, oficinas, atividades culturais ou esportivas. Sua opinião é fundamental para que possamos organizar um evento que atenda aos interesses de todos.",
                    "options": ["Palestras", "Oficinas", "Atividades culturais", "Atividades esportivas"]
                },
                {
                    "title": "Enquete 2",
                    "question": "Você apoia a criação de uma horta comunitária no bairro?",
                    "content": "Acredita que pode ajudar no abastecimento de alimentos frescos, promover a integração entre os moradores e incentivar hábitos saudáveis?",
                    "options": ["Sim, apoio!", "Não apoio", "Preciso de mais informações"]
                }
            ]
            from app.api.post.schemas import PollCreate
            for enquete in enquetes:
                poll = PollCreate(
                    post=PostCreate(
                        community_id=str(community.id),
                        user_id=str(user.id),
                        type_post=PostTypeEnum.POLL,
                        title=enquete["title"],
                        content=enquete["content"],
                        image_url=None,
                    ),
                    question=enquete["question"],
                    options=enquete["options"]
                )
                poll_response = post_service.create_poll(poll)
                print(f"Enquete '{poll_response.post.title}' criada com sucesso! ID: {poll_response.post.id}")
                posts.append(poll_response.post)

            # Anúncios
            anuncios_textos = [
                "Novo horário de funcionamento: agora abrimos aos sábados das 8h às 14h para melhor atender você e sua família. Aproveite para conhecer nossos novos serviços, participar de atividades especiais e traga seus amigos para um final de semana diferente. Estamos sempre buscando melhorar para oferecer o melhor atendimento e experiências para todos. Venha nos visitar e confira as novidades!",
                "Atenção: inscrições abertas para o curso gratuito de astronomia! Aprenda sobre planetas, estrelas, galáxias e os mistérios do universo com especialistas da área. O curso é voltado para todas as idades, com aulas teóricas e práticas, observação do céu e atividades interativas. Vagas limitadas, garanta já a sua e venha explorar o espaço conosco!"
            ]
            for i, texto in enumerate(anuncios_textos):
                post_data = PostCreate(
                    community_id=str(community.id),
                    user_id=str(user.id),
                    type_post=PostTypeEnum.ANNOUNCEMENT,
                    title=f"Anúncio {i+1}",
                    content=texto,
                    image_url=None,
                )
                post = post_service.create_post(post_data)
                print(f"Anúncio '{post.title}' criada com sucesso! ID: {post.id}")
                posts.append(post)

            # Adicionar comentários e replies em todos os posts
            comments = []
            # lista combinada de member_ids (CommunityMember.id) para atribuir comentários
            all_member_ids = [admin_member_id] + membros_member_ids + moderadores_member_ids
            if not all_member_ids:
                # fallback: usar o admin_member_id se por algum motivo não houver outros membros
                all_member_ids = [admin_member_id]
            for idx, post in enumerate(posts):
                # escolher um member_id em round-robin entre os membros criados
                selected_member_id = all_member_ids[idx % len(all_member_ids)]
                comment_data = CommentCreate(
                    post_id=str(post.id),
                    member_id=str(selected_member_id),
                    content=f"Comentário principal no post {idx+1}",
                    parent_id=None,
                )
                comment = comment_service.create_comment(comment_data)
                comments.append(comment)
                print(f"Comentário criado no post '{post.title}' (Post ID: {post.id}): {comment.content} (Comment ID: {comment.id})")

                reply_data = CommentCreate(
                    post_id=str(post.id),
                    member_id=str(selected_member_id),
                    content=f"Reply ao comentário no post {idx+1}",
                    parent_id=str(comment.id),
                )
                reply = comment_service.create_comment(reply_data)
                print(f"Reply criado: {reply.content} (Reply ID: {reply.id}) para o comentário {comment.id}")

            # Criar reports de posts
            print("\nCriando reports de posts...")
            from app.api.reports.service import ReportService
            from app.api.reports.schema import ReportCreate, ReportPostCreate, ReportReasonEnum, ReportTypeEnum
            
            report_service = ReportService(tm)
            
            for i, post in enumerate(posts[:2]):  # Exemplo: reportar os 2 primeiros posts
                try:
                    # Criar o reporte base
                    report_data = ReportCreate(
                        reporter_id=str(membros_member_ids[0] if membros_member_ids else admin_member_id),
                        type=ReportTypeEnum.POST_REPORT,
                        reason=ReportReasonEnum.INAPPROPRIATE_CONTENT,
                        description=f"Este post contém conteúdo inadequado e deve ser revisado."
                    )
                    report = report_service.create_report(report_data)
                    print(f"Report criado (ID: {report.id}) para o post '{post.title}'")
                    
                    # Criar a associação report-post
                    report_post_data = ReportPostCreate(
                        report_id=str(report.id),
                        post_id=str(post.id),
                        community_id=str(community.id)
                    )
                    report_service.create_report_post(report_post_data)
                    print(f"Post '{post.title}' (ID: {post.id}) reportado com sucesso!")
                except Exception as e:
                    print(f"Erro ao reportar post {post.id}: {e}")

            # Criar reports de comentários
            print("\nCriando reports de comentários...")
            from app.api.reports.schema import ReportCommentCreate
            
            for i, comment in enumerate(comments[:2]):  # Exemplo: reportar os 2 primeiros comentários
                try:
                    # Criar o reporte base
                    report_data = ReportCreate(
                        reporter_id=str(membros_member_ids[1] if len(membros_member_ids) > 1 else admin_member_id),
                        type=ReportTypeEnum.COMMENT_REPORT,
                        reason=ReportReasonEnum.HARASSMENT,
                        description=f"Este comentário contém linguagem ofensiva e viola as regras da comunidade."
                    )
                    report = report_service.create_report(report_data)
                    print(f"Report criado (ID: {report.id}) para o comentário (ID: {comment.id})")
                    
                    # Criar a associação report-comment
                    report_comment_data = ReportCommentCreate(
                        report_id=str(report.id),
                        comment_id=str(comment.id),
                        community_id=str(community.id)
                    )
                    report_service.create_report_comment(report_comment_data)
                    print(f"Comentário (ID: {comment.id}) reportado com sucesso!")
                except Exception as e:
                    print(f"Erro ao reportar comentário {comment.id}: {e}")
                    
            # Criar reports de membros/usuários
            print("\nCriando reports de membros...")
            from app.api.reports.schema import ReportMemberCreate
            
            # Reportar o primeiro membro comum
            if membros_member_ids:
                try:
                    report_data = ReportCreate(
                        reporter_id=str(moderadores_member_ids[0] if moderadores_member_ids else admin_member_id),
                        type=ReportTypeEnum.MEMBER_REPORT,
                        reason=ReportReasonEnum.SPAM,
                        description=f"Este usuário está enviando spam repetidamente na comunidade."
                    )
                    report = report_service.create_report(report_data)
                    print(f"Report criado (ID: {report.id}) para o membro (ID: {membros_member_ids[0]})")
                    
                    # Criar a associação report-member
                    report_member_data = ReportMemberCreate(
                        report_id=str(report.id),
                        member_id=str(membros_member_ids[0]),
                        community_id=str(community.id)
                    )
                    report_service.create_report_member(report_member_data)
                    print(f"Membro (ID: {membros_member_ids[0]}) reportado com sucesso!")
                except Exception as e:
                    print(f"Erro ao reportar membro {membros_member_ids[0]}: {e}")
    except Exception as e:
        print(f"Error creating community: {e}")

# Garante execução direta do script
if __name__ == "__main__":
    init_community()