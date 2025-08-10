import gi
import re
import json
import logging
import subprocess

# Inicializa notificações
gi.require_version("Notify", "0.7")
from gi.repository import Notify

# Imports do Ulauncher
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction

# Imports internos
from .card import Card
from .note import Note
from .identity import Identity
from .tipo_dado import TipoDado
from .credential import Credential

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)


class KeywordQueryEventListener(EventListener):

    def __init__(self, extension):
        self.extension = extension
        logger.info("Inicializando KeywordQueryEventListener")
        
        self.main_extension_kw = extension.preferences.get("main_kw", "bw")
        logger.info(f"Keyword para identificar que a extensão foi ativada: {self.main_extension_kw}")
        
        self.sync_kw = extension.preferences.get("sync_kw", "sync")
        logger.info(f"Keyword para sincronizar: {self.sync_kw}")
        
        self.lock_kw = extension.preferences.get("lock_kw", "lock")
        logger.info(f"Keyword para bloquear: {self.lock_kw}")
        
        self.unlock_kw = extension.preferences.get("unlock_kw", "unlock")
        logger.info(f"Keyword para desbloquear: {self.unlock_kw}")
        
    def on_event(self, event, extension):
        user_query = (event.get_argument() or "").strip()
        prompt = event.get_query().strip()

        logger.info(f"DEBUG - prompt recebido: '{prompt}'")
        logger.info(f"DEBUG - user_query: '{user_query}'")

        if not prompt.lower().startswith(f'{self.main_extension_kw.lower()}'):
            return RenderResultListAction([])

        pasta = None
        filtro_nome = ""

        if '/' in user_query:
            folder_match = re.search(r"/([a-zA-Z][\w\-\.]*)", user_query)
            if folder_match:
                pasta = folder_match.group(1)
                filtro_match = re.search(rf"/{re.escape(pasta)}\s+(.*)", user_query)
                filtro_nome = filtro_match.group(1).strip() if filtro_match else ""
            else:
                filtro_nome = user_query
        else:
            filtro_nome = user_query

        filtro_nome = filtro_nome.replace('"', '').strip().lower()

        if not self.validar_rbw_configurado():
            return RenderResultListAction([])

        vault_locked = self.rbw_bloqueado()
        items = []

        # 🔐 Se cofre estiver bloqueado, mostrar somente o botão de desbloquear
        if vault_locked:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/unlock.png',
                    name='Desbloquear cofre',
                    description='Clique para desbloquear o cofre do Bitwarden',
                    on_enter=ExtensionCustomAction({'action': 'unlock_vault'})
                )
            ])

        # ✅ Prompt totalmente vazio → mostrar ações básicas
        if not filtro_nome and not pasta:
            logger.info("Prompt vazio, mostrando ações principais")
            items.append(
                ExtensionResultItem(
                    icon='images/lock.png',
                    name='Bloquear cofre',
                    description='Trava o cofre do Bitwarden',
                    on_enter=ExtensionCustomAction({'action': 'lock_vault'})
                ))
            items.append(
                ExtensionResultItem(
                    icon='images/sync.png',
                    name='Sincronizar cofre',
                    description='Atualiza o cofre com o servidor remoto',
                    on_enter=ExtensionCustomAction({'action': 'sync_vault'})
                )
            )
            
        # 🔍 Verifica se está tentando completar nome de pasta
        match = re.search(r"/([^ /\n]*)$", prompt)
        logger.info(f"Match encontrado: { prompt }")
        if match or prompt == f'{ self.main_extension_kw } /':
            nome_potencial_pasta = match.group(1).lower()
            pastas_existentes = set(r['pasta'].lower() for r in self._buscar_registros_raw())

            if nome_potencial_pasta not in pastas_existentes or prompt == f'{ self.main_extension_kw } /':
                return RenderResultListAction(self.listar_pastas(prompt))
            else:
                logger.info(f"Pasta '{nome_potencial_pasta}' detectada como existente")

        # 🔍 Buscar registros filtrados
        registros = self._buscar_registros_raw(pasta, filtro_nome)

        # 📌 Registro exato
        registro_exato = next((r for r in registros if r['nome'].lower() == filtro_nome), None)
        if registro_exato:
            detalhes = self._buscar_detalhes_item(registro_exato['id'])
            return RenderResultListAction(detalhes)

        # 📌 Apenas um resultado? Mostrar direto
        if len(registros) == 1 and registros[0]['nome'].strip().lower() == filtro_nome:
            detalhes = self._buscar_detalhes_item(registros[0]['id'])
            return RenderResultListAction(detalhes)

        # 📋 Mostrar lista dos resultados encontrados
        for r in registros:
            nome = r['nome']
            new_query = self.substituir_ultimo_termo(prompt, nome)
            items.append(ExtensionResultItem(
                icon='images/arquivo.png',
                name=nome,
                description=f"Pasta: {r['pasta']}" if r['pasta'] else "",
                on_enter=SetUserQueryAction(new_query)
            ))
            

        return RenderResultListAction(items)

    def show_notification(self, message, title="Ulauncher Extension"):
        Notify.init("Ulauncher Extension")
        notification = Notify.Notification.new(title, message)
        logger.info(f"Exibindo notificação: {title} - {message}")
        notification.show()

    def validar_rbw_configurado(self):
        try:
            result = subprocess.run(['rbw', 'config', 'show'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            output = result.stdout.decode('utf-8').strip()

            for line in output.splitlines():
                if "email" in line:
                    email = line.split(":", 1)[-1].strip().replace('"', '').replace(',', '')
                    if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                        logger.info(f"'rbw' configurado corretamente com email: {email}")
                        return True

            self.show_notification("'rbw' n\u00e3o est\u00e1 configurado corretamente.", "Erro")
        except Exception as e:
            if 'Arquivo ou diret\u00f3rio inexistente: \'rbw\'' in str(e):
                self.show_notification("'rbw' n\u00e3o est\u00e1 instalado ou n\u00e3o est\u00e1 no PATH.", "Erro")
            else:
                self.show_notification(f"Erro: {str(e)}", "Erro")

        return False

    def rbw_bloqueado(self):
        try:
            subprocess.run(['rbw', 'unlocked'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            logger.info("O cofre 'rbw' est\u00e1 desbloqueado.")
            return False
        except subprocess.CalledProcessError as e:
            if 'agent is locked' in e.stderr.decode('utf-8'):
                logger.info("O cofre 'rbw' est\u00e1 bloqueado.")
                return True
            self.show_notification(f"Erro ao verificar lock: {e.stderr.decode('utf-8')}", "Erro")
        except Exception as e:
            self.show_notification(f"Erro inesperado: {str(e)}", "Erro")

        return False

    def bloquear_rbw(self):
        self._executar_comando(['rbw', 'lock'], "Cofre bloqueado com sucesso!")

    def desbloquear_rbw(self):
        self._executar_comando(['rbw', 'unlock'], "Cofre desbloqueado com sucesso!")

    def sync_rbw(self):
        self._executar_comando(['rbw', 'sync'], "Cofre atualizado com sucesso!")

    def _executar_comando(self, comando, mensagem_sucesso):
        try:
            subprocess.run(comando, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            self.show_notification(mensagem_sucesso, "Sucesso")
        except Exception as e:
            self.show_notification(f"Erro: {str(e)}", "Erro")

    def get_info(self, item_id):
        try:
            result = subprocess.run(['rbw', 'get', '--raw', item_id], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            raw_output = result.stdout.decode('utf-8').strip()

            tipo_dado = self.determinar_tipo_objeto(raw_output)
            logger.info(f"O registro [{ item_id }] = [{tipo_dado}]")
            items = {
                TipoDado.CREDENCIAL: Credential,
                TipoDado.CARTAO: Card,
                TipoDado.IDENTIDADE: Identity
            }.get(tipo_dado, Note)(raw_output).get_itens()
            logger.info(f"Quantia de dados retornados: {len(items)}")

            return RenderResultListAction(items)

        except json.JSONDecodeError as e:
            self.show_notification(f"Erro de JSON: {str(e)}", "Erro")
        except Exception as e:
            self.show_notification(f"Erro geral: {str(e)}", "Erro")

        return RenderResultListAction([])

    def listar_pastas(self, user_query_prefix=""):
        items = []
        try:
            match = re.search(r"/([^ /\n]*)$", user_query_prefix)
            filtro = match.group(1).lower() if match else ""
            
            logger.info(f"Listando pastas com filtro: '{filtro}'")

            result = subprocess.run(
                "rbw list --fields folder | grep -v '^$' | sort | uniq",
                shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5
            )

            for folder in result.stdout.decode('utf-8').strip().splitlines():
                folder = folder.strip()
                if folder.lower().startswith(filtro):
                    new_query = re.sub(r"/[^ /\n]*$", f"/{folder} ", user_query_prefix)
                    items.append(ExtensionResultItem(
                        icon='images/pasta.png',
                        name=folder,
                        description=f'Pasta: {folder}',
                        on_enter=SetUserQueryAction(new_query)
                    ))
        except Exception as e:
            self.show_notification(f"Erro: {str(e)}", "Erro")

        return items

    def _buscar_registros_raw(self, pasta=None, filtro_nome=""):
        registros = []
        try:
            result = subprocess.run("rbw list --fields name,folder,id", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            linhas = result.stdout.decode('utf-8').strip().splitlines()

            for linha in linhas:
                partes = linha.strip().split('\t')
                if len(partes) < 3:
                    continue
                nome, pasta_item, item_id = partes[0].strip(), partes[1].strip(), partes[2].strip()

                if pasta and pasta.lower() != pasta_item.lower():
                    continue

                if filtro_nome and filtro_nome.lower() not in nome.lower():
                    continue

                registros.append({'nome': nome, 'pasta': pasta_item, 'id': item_id})
        except Exception as e:
            self.show_notification(f"Erro: {str(e)}", "Erro")

        return registros

    def _buscar_detalhes_item(self, item_id):
        try:
            result = subprocess.run(['rbw', 'get', '--raw', item_id], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            raw_output = result.stdout.decode('utf-8').strip().replace('\\', '\\\\')
            data = json.loads(raw_output)

            tipo_dado = self.determinar_tipo_objeto(data)
            cls = {
                TipoDado.CREDENCIAL: Credential,
                TipoDado.CARTAO: Card,
                TipoDado.IDENTIDADE: Identity
            }.get(tipo_dado, Note)

            return cls(data).get_itens()
        except Exception as e:
            self.show_notification(f"Erro ao buscar detalhes: {str(e)}", "Erro")
            return []

    def determinar_tipo_objeto(self, obj):
        data = obj.get("data")
        notes = obj.get("notes")

        if not isinstance(data, dict):
            data = {}
        if not isinstance(notes, str):
            notes = ""

        if "cardholder_name" in data:
            return TipoDado.CARTAO
        elif all(k in data for k in ["first_name", "middle_name", "last_name"]):
            return TipoDado.IDENTIDADE
        elif "username" in data and not any(k in data for k in ["first_name", "middle_name", "last_name"]):
            return TipoDado.CREDENCIAL
        elif notes:
            return TipoDado.NOTA

        return TipoDado.NOTA

    def substituir_ultimo_termo(self, prompt, novo_termo):
        partes = prompt.rstrip().split(' ')
        pasta_informada = False

        if len(partes) > 1:
            if re.match(r'^/\w+$', partes[1].lower()):
                pasta_informada = True

            if pasta_informada and len(partes) > 2:
                partes.pop(1)

            if partes[1].lower() in novo_termo.lower():
                partes.pop(1)

            return ' '.join(partes) + " " + novo_termo
        else:
            return prompt + novo_termo + ' '

    