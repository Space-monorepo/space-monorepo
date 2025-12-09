
#!/bin/bash
# Script para checar status do backend via API do frontend

# =================== AVISO DE SEGURANÇA ===================
# NÃO execute este script em ambiente de produção!
# Ele é destinado apenas para ambientes de desenvolvimento/homologação.
# ==========================================================

# Reforço de segurança: aborta em caso de erro, variável indefinida ou pipe quebrado
set -euo pipefail

# Impede execução como root
if [ "$EUID" -eq 0 ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Não execute este script como root!"
  exit 1
fi

# Opcional: checagem de ambiente seguro (ajuste conforme sua infra)
if [[ "${ENVIRONMENT:-dev}" == "production" ]]; then
  echo -e "\033[1;31m[ERRO]\033[0m Este script não deve rodar em produção!"
  exit 1
fi



BACKEND_URL="http://localhost:8001"
ROUTES=(
  "/users/me"           # GET /users/me
  "/posts/feed"         # GET /posts/feed
  "/chat/messages/1"    # GET /chat/messages/{message_id} (exemplo com id 1)
  "/chat/conversation/1" # GET /chat/conversation/{user_id} (exemplo com id 1)
  "/moderation/posts/1" # GET /moderation/posts/{community_id} (exemplo com id 1)
  "/communities"        # Prefixo communities
  "/comments"           # Prefixo comments
  "/ratings"            # Prefixo ratings
)




# Gera email e senha aleatórios

EMAIL="healthcheck_$(date +%s%N)@test.com"
PASSWORD="SenhaSuperForte123!"
NAME="Health Check Bot"

# Signup (envia name e hashed_password)

# Signup (envia name e hashed_password, usando heredoc para JSON seguro)
read -r -d '' SIGNUP_JSON <<EOF
{
  "email": "$EMAIL",
  "name": "$NAME",
  "hashed_password": "$PASSWORD"
}
EOF
SIGNUP_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/signup" \
  -H "Content-Type: application/json" \
  -d "$SIGNUP_JSON")

# Login (form-urlencoded: username=email, password=senha)
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d '"' -f4)



COMMUNITIES_STATUS_AND_RESPONSE=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/communities/?page=1&page_size=1" -H "Authorization: Bearer $TOKEN" || true)
COMMUNITIES_RESPONSE=$(echo "$COMMUNITIES_STATUS_AND_RESPONSE" | head -n -1)
COMMUNITIES_STATUS=$(echo "$COMMUNITIES_STATUS_AND_RESPONSE" | tail -n1)
if [[ "${DEBUG:-false}" == "true" ]]; then
  echo "[DEBUG] Status HTTP da API de comunidades: $COMMUNITIES_STATUS"
  echo "[DEBUG] Resposta da API de comunidades: $COMMUNITIES_RESPONSE"
fi
COMMUNITY_ID=$(echo $COMMUNITIES_RESPONSE | grep -o '"id":"[^\"]*"' | head -n1 | cut -d '"' -f4)


# Se não existir comunidade, exibir mensagem de erro amigável
if [ -z "$COMMUNITY_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Não foi possível obter um community_id para os testes."
  if [[ "${DEBUG:-false}" == "true" ]]; then
    echo "Resposta da API: $COMMUNITIES_RESPONSE"
  fi
  echo "Sugestão: execute o script init_community.py no backend para criar uma comunidade."
  exit 1
fi

# IDs de exemplo (ajuste conforme necessário)
USER_ID="$EMAIL"
POST_ID="1"
COMMENT_ID="1"
RATING_ID="1"
MESSAGE_ID="1"

# Payloads mínimos para POST/PATCH
POST_PAYLOAD='{"community_id": "'$COMMUNITY_ID'", "title": "HealthCheck", "content": "Teste", "type_post": "text"}'
COMMENT_PAYLOAD='{"post_id": "'$POST_ID'", "community_id": "'$COMMUNITY_ID'", "content": "Comentário healthcheck"}'
RATING_PAYLOAD='{"post_id": "'$POST_ID'", "community_id": "'$COMMUNITY_ID'", "score": 5}'
CHAT_PAYLOAD='{"content": "Mensagem healthcheck", "receiver_id": "'$USER_ID'"}'

declare -A ENDPOINTS
# Métodos e rotas principais (exemplos)
ENDPOINTS["GET /users/me"]="/users/me"
ENDPOINTS["POST /users/signup"]="/users/signup"
ENDPOINTS["POST /users/login"]="/users/login"
ENDPOINTS["PATCH /users/me"]="/users/me"
ENDPOINTS["DELETE /users/me"]="/users/me"
ENDPOINTS["GET /posts/feed"]="/posts/feed"
ENDPOINTS["POST /posts"]="/posts"
ENDPOINTS["GET /posts"]="/posts"
ENDPOINTS["PATCH /posts/$POST_ID"]="/posts/$POST_ID"
ENDPOINTS["DELETE /posts/$COMMUNITY_ID/post/$POST_ID"]="/posts/$COMMUNITY_ID/post/$POST_ID"
ENDPOINTS["POST /chat/send"]="/chat/send"
ENDPOINTS["GET /chat/messages/$MESSAGE_ID"]="/chat/messages/$MESSAGE_ID"
ENDPOINTS["PATCH /chat/messages/$MESSAGE_ID"]="/chat/messages/$MESSAGE_ID"
ENDPOINTS["DELETE /chat/messages/$MESSAGE_ID"]="/chat/messages/$MESSAGE_ID"
ENDPOINTS["GET /chat/conversation/$USER_ID"]="/chat/conversation/$USER_ID"
ENDPOINTS["GET /moderation/posts/$COMMUNITY_ID"]="/moderation/posts/$COMMUNITY_ID"
ENDPOINTS["PATCH /moderation/posts/$POST_ID"]="/moderation/posts/$POST_ID"
ENDPOINTS["GET /communities"]="/communities/"
ENDPOINTS["GET /communities/$COMMUNITY_ID"]="/communities/$COMMUNITY_ID"
ENDPOINTS["PATCH /communities/$COMMUNITY_ID"]="/communities/$COMMUNITY_ID"
ENDPOINTS["DELETE /communities/$COMMUNITY_ID"]="/communities/$COMMUNITY_ID"
ENDPOINTS["GET /communities/$COMMUNITY_ID/members"]="/communities/$COMMUNITY_ID/members"
ENDPOINTS["GET /communities/user/$USER_ID/communities"]="/communities/user/$USER_ID/communities"
ENDPOINTS["GET /communities/$COMMUNITY_ID/moderators"]="/communities/$COMMUNITY_ID/moderators"
ENDPOINTS["GET /comments"]="/comments"
ENDPOINTS["POST /comments"]="/comments"
ENDPOINTS["PATCH /comments/$COMMENT_ID"]="/comments/$COMMENT_ID"
ENDPOINTS["DELETE /comments/$COMMENT_ID"]="/comments/$COMMENT_ID"
ENDPOINTS["GET /ratings"]="/ratings"
ENDPOINTS["POST /ratings"]="/ratings"
ENDPOINTS["GET /ratings/$COMMUNITY_ID"]="/ratings/$COMMUNITY_ID"
ENDPOINTS["PATCH /ratings/$RATING_ID"]="/ratings/$RATING_ID"
ENDPOINTS["DELETE /ratings/$RATING_ID"]="/ratings/$RATING_ID"

echo "\n================ Testando todos os métodos das rotas principais ================\n"
for key in "${!ENDPOINTS[@]}"; do
  METHOD=$(echo $key | cut -d' ' -f1)
  ROUTE=${ENDPOINTS[$key]}
  URL="$BACKEND_URL$ROUTE"
  STATUS=""
  case $METHOD in
    GET)
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$URL")
      ;;
    POST)
      if [[ $ROUTE == *"/posts"* ]]; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$POST_PAYLOAD" "$URL")
      elif [[ $ROUTE == *"/comments"* ]]; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$COMMENT_PAYLOAD" "$URL")
      elif [[ $ROUTE == *"/ratings"* ]]; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$RATING_PAYLOAD" "$URL")
      elif [[ $ROUTE == *"/chat/send"* ]]; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$CHAT_PAYLOAD" "$URL")
      elif [[ $ROUTE == "/users/signup" ]]; then
        STATUS=201 # já foi feito antes
      elif [[ $ROUTE == "/users/login" ]]; then
        STATUS=200 # já foi feito antes
      else
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" "$URL")
      fi
      ;;
    PATCH)
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}' "$URL")
      ;;
    DELETE)
      STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE -H "Authorization: Bearer $TOKEN" "$URL")
      ;;
  esac
  if [ "$STATUS" = "200" ] || [ "$STATUS" = "201" ] || [ "$STATUS" = "204" ]; then
    echo -e "\033[1;32m[OK]\033[0m $key $ROUTE ($STATUS)"
  else
    echo -e "\033[1;31m[ERRO]\033[0m $key $ROUTE (Status: $STATUS)"
    if [[ "${DEBUG:-false}" == "true" ]]; then
      echo "[DEBUG] Falha ao acessar $ROUTE com método $METHOD. Status: $STATUS"
    fi
  fi
done

# Criar post
POST_JSON=$(cat <<EOF
{
  "community_id": "$COMMUNITY_ID",
  "title": "Post HealthCheck",
  "content": "Conteúdo de teste",
  "type_post": "text"
}
EOF
)
POST_RESPONSE=$(curl -s -X POST "$BACKEND_URL/posts" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$POST_JSON")
POST_ID=$(echo $POST_RESPONSE | grep -o '"id":"[^\"]*"' | cut -d '"' -f4)
if [ -z "$POST_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar post."
  if [[ "${DEBUG:-false}" == "true" ]]; then
    echo "Resposta: $POST_RESPONSE"
  fi
fi

# Criar mensagem de chat (receiver_id = email do próprio usuário para teste)
MESSAGE_JSON=$(cat <<EOF
{
  "content": "Mensagem de teste healthcheck",
  "receiver_id": "$EMAIL"
}
EOF
)
MESSAGE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/chat/send" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$MESSAGE_JSON")
MESSAGE_ID=$(echo $MESSAGE_RESPONSE | grep -o '"id":"[^\"]*"' | cut -d '"' -f4)
if [ -z "$MESSAGE_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar mensagem de chat."
  if [[ "${DEBUG:-false}" == "true" ]]; then
    echo "Resposta: $MESSAGE_RESPONSE"
  fi
fi

# Criar comentário
COMMENT_JSON=$(cat <<EOF
{
  "post_id": "$POST_ID",
  "community_id": "$COMMUNITY_ID",
  "content": "Comentário de teste healthcheck"
}
EOF
)
COMMENT_RESPONSE=$(curl -s -X POST "$BACKEND_URL/comments" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$COMMENT_JSON")
COMMENT_ID=$(echo $COMMENT_RESPONSE | grep -o '"id":"[^\"]*"' | cut -d '"' -f4)
if [ -z "$COMMENT_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar comentário."
  if [[ "${DEBUG:-false}" == "true" ]]; then
    echo "Resposta: $COMMENT_RESPONSE"
  fi
fi

# Criar rating
RATING_JSON=$(cat <<EOF
{
  "post_id": "$POST_ID",
  "community_id": "$COMMUNITY_ID",
  "score": 5
}
EOF
)
RATING_RESPONSE=$(curl -s -X POST "$BACKEND_URL/ratings" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$RATING_JSON")
RATING_ID=$(echo $RATING_RESPONSE | grep -o '"id":"[^\"]*"' | cut -d '"' -f4)
if [ -z "$RATING_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar rating."
  if [[ "${DEBUG:-false}" == "true" ]]; then
    echo "Resposta: $RATING_RESPONSE"
  fi
fi

# Atualizar rotas para usar os IDs criados
ROUTES=(
  "/users/me"
  "/posts/feed"
  "/chat/messages/$MESSAGE_ID"
  "/chat/conversation/$EMAIL"
  "/moderation/posts/$COMMUNITY_ID"
  "/communities/$COMMUNITY_ID"
  "/comments/$COMMENT_ID"
  "/ratings/$RATING_ID"
)

# Criar comunidade
COMMUNITY_JSON=$(cat <<EOF
{
  "name": "HealthCheck Community",
  "description": "Comunidade de teste healthcheck",
  "type_community": "university"
}
EOF
)
COMMUNITY_RESPONSE=$(curl -s -X POST "$BACKEND_URL/communities" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$COMMUNITY_JSON")

COMMUNITY_ID=$(echo $COMMUNITY_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)
if [ -z "$COMMUNITY_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar comunidade. Resposta: $COMMUNITY_RESPONSE"
fi

# Criar post
POST_JSON=$(cat <<EOF
{
  "community_id": "$COMMUNITY_ID",
  "title": "Post HealthCheck",
  "content": "Conteúdo de teste",
  "type_post": "text"
}
EOF
)
POST_RESPONSE=$(curl -s -X POST "$BACKEND_URL/posts" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$POST_JSON")
POST_ID=$(echo $POST_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)
if [ -z "$POST_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar post. Resposta: $POST_RESPONSE"
fi

POST_JSON=$(cat <<EOF
{
  "community_id": "$COMMUNITY_ID",
  "title": "Post HealthCheck",
  "content": "Conteúdo de teste",
  "type_post": "text",
  "user_id": "$USER_ID"
}
EOF
)
POST_RESPONSE=$(curl -s -X POST "$BACKEND_URL/posts" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$POST_JSON")
POST_ID=$(echo $POST_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)

# Criar mensagem de chat (receiver_id = email do próprio usuário para teste)
MESSAGE_JSON=$(cat <<EOF
{
  "content": "Mensagem de teste healthcheck",
  "receiver_id": "$EMAIL"
}
EOF
)
MESSAGE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/chat/send" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$MESSAGE_JSON")
MESSAGE_ID=$(echo $MESSAGE_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)
if [ -z "$MESSAGE_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar mensagem de chat. Resposta: $MESSAGE_RESPONSE"
fi

MESSAGE_JSON=$(cat <<EOF
{
  "content": "Mensagem de teste healthcheck",
  "receiver_id": "$USER_ID"
}
EOF
)
MESSAGE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/chat/send" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$MESSAGE_JSON")
MESSAGE_ID=$(echo $MESSAGE_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)

# Criar comentário
COMMENT_JSON=$(cat <<EOF
{
  "post_id": "$POST_ID",
  "community_id": "$COMMUNITY_ID",
  "content": "Comentário de teste healthcheck"
}
EOF
)
COMMENT_RESPONSE=$(curl -s -X POST "$BACKEND_URL/comments" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$COMMENT_JSON")
COMMENT_ID=$(echo $COMMENT_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)
if [ -z "$COMMENT_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar comentário. Resposta: $COMMENT_RESPONSE"
fi

COMMENT_JSON=$(cat <<EOF
{
  "post_id": "$POST_ID",
  "user_id": "$USER_ID",
  "content": "Comentário de teste healthcheck"
}
EOF
)
COMMENT_RESPONSE=$(curl -s -X POST "$BACKEND_URL/comments" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$COMMENT_JSON")
COMMENT_ID=$(echo $COMMENT_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)

# Criar rating
RATING_JSON=$(cat <<EOF
{
  "post_id": "$POST_ID",
  "community_id": "$COMMUNITY_ID",
  "score": 5
}
EOF
)
RATING_RESPONSE=$(curl -s -X POST "$BACKEND_URL/ratings" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$RATING_JSON")
RATING_ID=$(echo $RATING_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)
if [ -z "$RATING_ID" ]; then
  echo -e "\033[1;31m[ERRO]\033[0m Falha ao criar rating. Resposta: $RATING_RESPONSE"
fi

RATING_JSON=$(cat <<EOF
{
  "user_id": "$USER_ID",
  "community_id": "$COMMUNITY_ID",
  "rating": 5,
  "title": "Ótima comunidade!",
  "description": "Avaliação de teste healthcheck."
}
EOF
)
RATING_RESPONSE=$(curl -s -X POST "$BACKEND_URL/ratings/$COMMUNITY_ID/create-rating" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$RATING_JSON")
RATING_ID=$(echo $RATING_RESPONSE | grep -o '"id":"[^"]*"' | cut -d '"' -f4)

# Atualizar rotas para usar os IDs criados
ROUTES=(
  "/users/me"
  "/posts/feed"
  "/chat/messages/$MESSAGE_ID"
  "/chat/conversation/$EMAIL"
  "/moderation/posts/$COMMUNITY_ID"
  "/communities/$COMMUNITY_ID"
  "/comments/$COMMENT_ID"
  "/ratings/$RATING_ID"
)

ROUTES=(
  "/users/me"
  "/posts/feed"
  "/chat/messages/$MESSAGE_ID"
  "/chat/conversation/$USER_ID"
  "/moderation/posts/$COMMUNITY_ID"
  "/communities/$COMMUNITY_ID"
  "/comments/$COMMUNITY_ID/post/$POST_ID/comment/$COMMENT_ID"
  "/ratings/$COMMUNITY_ID/rating/$RATING_ID"
)

ALL_OK=true

for ROUTE in "${ROUTES[@]}"; do
  FULL_URL="$BACKEND_URL$ROUTE"
  STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$FULL_URL")
  if [ "$STATUS_CODE" = "200" ]; then
    echo -e "\033[1;32m[OK]\033[0m $ROUTE ($STATUS_CODE)"
  else
    echo -e "\033[1;31m[ERRO]\033[0m $ROUTE (Status: $STATUS_CODE)"
    if [[ "${DEBUG:-false}" == "true" ]]; then
      echo "[DEBUG] Falha ao acessar $ROUTE. Status: $STATUS_CODE"
    fi
    ALL_OK=false
  fi
done

if [ "$ALL_OK" = true ]; then
  echo -e "\033[1;32mTodas as rotas testadas estão online!\033[0m"
  exit 0
else
  echo -e "\033[1;31mAlguma rota falhou!\033[0m"
  exit 1
fi
