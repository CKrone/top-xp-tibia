<h1>Sobre o Projeto</h1>

Atualmente o projeto consiste em automações de mensagens via Whatsapp. Mensagens estas relacionadas ao jogo MMORPG Tibia.

<h1>Scripts</h1>

<h3>send_msg_top_xp_guild</h3>

Este script busca a lista de todos os membros da guilda e salva em um excel. Depois faz a busca de todos os membros da guilda que estão na lista de Highscores de experiência do Tibia. Essa busca é feita pelo mundo e por vocação, Knight, Paladin, Sorcerer, Druid e Monk,
para conseguir abranger todos os jogadores. Após fazer a busca desta lista teremos a informação da experiência máxima do jogador que será comparada com a experiência máxima do dia anterior e o resultado da subtração desse valor será o total de experiência que o jogador conseguiu
no dia anterior à execução. É feito o cálculo para todos membros e com mais algumas informações é salvo em um arquivo .json do dia que servirá de histórico e base para cálculo do dia seguinte. Em seguida o script ordenada essa lista pela maior quantidade de experiência
obtida para a menor e restringe a lista em apenas 20 membros, top 20. Neste momento o script abre o navegador, acessa a página do Whatsapp busca o grupo da guild e envia a lista dos 20 membros, colocando a posição, nome, level e quantidade de experiência obtida, no fim da
mensagem adiciona uma linha informando o total de experiência da guilda, isso englobando todos os membros não só o top 20.
