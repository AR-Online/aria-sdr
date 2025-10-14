#!/usr/bin/env python3
"""
ARIA-SDR AgentOS - Implementacao Otimizada com AgentOSConfig
Baseado na documentacao oficial do Agno AgentOS
"""

import os
from textwrap import dedent
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.db.postgres import PostgresDb
from agno.memory.manager import MemoryManager
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.os.app import AgentOS
from agno.os.config import (
    AgentOSConfig,
    ChatConfig,
    DatabaseConfig,
    MemoryConfig,
    MemoryDomainConfig,
    SessionConfig,
    MetricsConfig,
    KnowledgeConfig,
    EvalsConfig,
)
from agno.os.interfaces.whatsapp import Whatsapp
from agno.tools.googlesearch import GoogleSearchTools

class ARIA_SDR_AgentOS_Optimized:
    """Classe principal para o AgentOS ARIA-SDR otimizada"""
    
    def __init__(self):
        self.agent_os = None
        self.agent = None
        self.business_db = None
        
    def create_databases(self):
        """Cria bancos de dados baseado no ambiente"""
        env = os.getenv("APP_ENV", "development")
        
        if env == "production":
            # PostgreSQL para produção
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL é obrigatória em produção")
            main_db = PostgresDb(db_url=db_url)
            business_db = PostgresDb(db_url=db_url)
        else:
            # SQLite para desenvolvimento
            main_db = SqliteDb(db_file="tmp/aria_agents.db")
            business_db = SqliteDb(db_file="tmp/aria_business.db")
        
        self.business_db = business_db
        return main_db
    
    def create_model(self):
        """Cria modelo baseado na configuração"""
        model_provider = os.getenv("MODEL_PROVIDER", "openai")
        model_id = os.getenv("MODEL_ID", "gpt-4o-mini")
        
        if model_provider == "openai":
            return OpenAIChat(id=model_id)
        elif model_provider == "google":
            return Gemini(id=model_id)
        else:
            # Fallback para OpenAI
            return OpenAIChat(id="gpt-4o-mini")
    
    def create_memory_manager(self, model):
        """Cria gerenciador de memória"""
        return MemoryManager(
            memory_capture_instructions=dedent("""
                Collect User's name,
                Collect Information about user's passion and hobbies,
                Collect Information about the users likes and dislikes,
                Collect information about what the user is doing with their life right now,
                Collect information about their business needs and volume requirements
            """),
            model=model,
        )
    
    def create_aria_agent(self):
        """Cria o agente ARIA-SDR principal"""
        
        # Componentes base
        db = self.create_databases()
        model = self.create_model()
        memory_manager = self.create_memory_manager(model)
        
        # Instruções do agente
        instructions = dedent("""
            Você é a ARIA, Agente de Relacionamento Inteligente da AR Online.
            
            Suas responsabilidades:
            1. Atender clientes via WhatsApp e chat web
            2. Classificar volumetria de envios (alto/baixo volume)
            3. Roteamento inteligente para FAQ, agendamento ou loja
            4. Responder em português brasileiro de forma cordial e objetiva
            
            Regras de negócio:
            - Volume alto: >= 1200 mensagens/mês → Agendamento
            - Volume baixo: < 1200 mensagens/mês → Loja
            - Use contexto fornecido quando disponível
            - Se não souber algo, ofereça encaminhar ao time
            
            Primeiro se apresente e pergunte o nome do usuário, depois pergunte sobre:
            - Seus hobbies e interesses
            - O que gosta de fazer
            - Sobre o que gosta de conversar
            - Suas necessidades de negócio
            
            Use a ferramenta Google Search para encontrar informações atualizadas sobre os tópicos da conversa.
            
            Sempre seja cordial, objetivo e profissional.
        """)
        
        # Criar agente
        self.agent = Agent(
            name="ARIA-SDR",
            model=model,
            tools=[GoogleSearchTools()],
            db=db,
            memory_manager=memory_manager,
            enable_agentic_memory=True,
            add_history_to_context=True,
            num_history_runs=3,
            add_datetime_to_context=True,
            markdown=True,
            instructions=instructions,
            debug_mode=os.getenv("APP_ENV") == "development",
        )
        
        return self.agent
    
    def create_interfaces(self):
        """Cria interfaces baseadas na configuração"""
        interfaces = []
        
        # Interface WhatsApp
        whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        if whatsapp_token:
            whatsapp_interface = Whatsapp(agent=self.agent)
            interfaces.append(whatsapp_interface)
            print("OK: Interface WhatsApp configurada")
        else:
            print("AVISO: WhatsApp não configurado - apenas chat web disponível")
        
        return interfaces
    
    def create_agentos_config(self):
        """Cria configuração otimizada do AgentOS"""
        
        return AgentOSConfig(
            chat=ChatConfig(
                quick_prompts={
                    "ARIA-SDR": [
                        "Qual é o seu volume mensal de mensagens?",
                        "Precisa de agendamento ou compra de créditos?",
                        "Como posso ajudar com seu negócio?",
                        "Conte-me sobre suas necessidades de comunicação",
                        "Qual é o seu principal desafio atual?"
                    ]
                }
            ),
            memory=MemoryConfig(
                dbs=[
                    DatabaseConfig(
                        db_id="aria-sdr-db",
                        domain_config=MemoryDomainConfig(
                            display_name="Memórias dos usuários ARIA-SDR"
                        )
                    ),
                    DatabaseConfig(
                        db_id="aria-business-db",
                        domain_config=MemoryDomainConfig(
                            display_name="Dados de negócio e volumetria"
                        )
                    )
                ]
            ),
            session=SessionConfig(
                display_name="Sessões ARIA-SDR",
                auto_cleanup_days=30
            ),
            metrics=MetricsConfig(
                display_name="Métricas ARIA-SDR",
                retention_days=90
            ),
            knowledge=KnowledgeConfig(
                display_name="Base de Conhecimento ARIA",
                max_file_size_mb=10
            ),
            evals=EvalsConfig(
                display_name="Avaliações ARIA-SDR",
                auto_eval_enabled=True
            )
        )
    
    def create_agent_os(self):
        """Cria o AgentOS principal com configuração otimizada"""
        
        # Criar agente
        self.create_aria_agent()
        
        # Criar interfaces
        interfaces = self.create_interfaces()
        
        # Criar configuração
        config = self.create_agentos_config()
        
        # Configurações do AgentOS
        agent_os_params = {
            "id": "aria-sdr-os",
            "name": "ARIA-SDR AgentOS",
            "description": "Sistema de Relacionamento Inteligente da AR Online",
            "version": "1.0.0",
            "telemetry": True,
            "enable_mcp_server": False,
            "on_route_conflict": "preserve_agentos"
        }
        
        # Criar AgentOS
        self.agent_os = AgentOS(
            **agent_os_params,
            agents=[self.agent],
            interfaces=interfaces,
            config=config,
        )
        
        return self.agent_os
    
    def get_app(self):
        """Obtém o app FastAPI"""
        if not self.agent_os:
            self.create_agent_os()
        return self.agent_os.get_app()
    
    def get_config(self):
        """Obtém a configuração atual do AgentOS"""
        if not self.agent_os:
            self.create_agent_os()
        
        # Acessar endpoint de configuração
        app = self.get_app()
        
        # Simular requisição para obter configuração
        import json
        config_data = {
            "os_id": "aria-sdr-os",
            "description": "Sistema de Relacionamento Inteligente da AR Online",
            "databases": ["aria-sdr-db", "aria-business-db"],
            "agents": ["ARIA-SDR"],
            "interfaces": ["WhatsApp"] if os.getenv("WHATSAPP_ACCESS_TOKEN") else [],
            "chat": {
                "quick_prompts": {
                    "ARIA-SDR": [
                        "Qual é o seu volume mensal de mensagens?",
                        "Precisa de agendamento ou compra de créditos?",
                        "Como posso ajudar com seu negócio?"
                    ]
                }
            },
            "memory": {
                "dbs": [
                    {
                        "db_id": "aria-sdr-db",
                        "domain_config": {
                            "display_name": "Memórias dos usuários ARIA-SDR"
                        }
                    },
                    {
                        "db_id": "aria-business-db",
                        "domain_config": {
                            "display_name": "Dados de negócio e volumetria"
                        }
                    }
                ]
            }
        }
        
        return config_data
    
    def serve(self, host: str = "localhost", port: int = 7777, reload: bool = True):
        """Inicia o servidor AgentOS"""
        
        if not self.agent_os:
            self.create_agent_os()
        
        print("ARIA-SDR AgentOS - Iniciando servidor otimizado")
        print("=" * 60)
        print(f"Agente: {self.agent.name}")
        print(f"Modelo: {self.agent.model}")
        print(f"Ferramentas: {len(self.agent.tools)}")
        print(f"Interfaces: {len(self.agent_os.interfaces)}")
        print(f"Endpoint: http://{host}:{port}")
        print("=" * 60)
        print("\nRecursos disponíveis:")
        print("• Chat com prompts rápidos")
        print("• Memória persistente")
        print("• Métricas e sessões")
        print("• Base de conhecimento")
        print("• Avaliações automáticas")
        print("=" * 60)
        print("\nPara conectar ao Control Plane:")
        print(f"1. Acesse: https://platform.agno.com")
        print(f"2. Adicione novo OS: http://{host}:{port}")
        print(f"3. Nome: ARIA-SDR Development")
        print("=" * 60)
        
        # Iniciar servidor
        self.agent_os.serve(
            app="aria_agentos_config_optimized:app",
            host=host,
            port=port,
            reload=reload
        )

def main():
    """Função principal"""
    
    print("ARIA-SDR - Inicializando AgentOS Otimizado com Configuração")
    print("Baseado na documentação oficial do Agno")
    print("=" * 60)
    
    try:
        # Criar instância do AgentOS
        aria_os = ARIA_SDR_AgentOS_Optimized()
        
        # Obter configurações do ambiente
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "7777"))
        reload = os.getenv("APP_ENV") == "development"
        
        # Mostrar configuração
        config = aria_os.get_config()
        print("\nConfiguração do AgentOS:")
        print(f"• OS ID: {config['os_id']}")
        print(f"• Descrição: {config['description']}")
        print(f"• Bancos: {len(config['databases'])}")
        print(f"• Agentes: {len(config['agents'])}")
        print(f"• Interfaces: {len(config['interfaces'])}")
        
        # Iniciar servidor
        aria_os.serve(host=host, port=port, reload=reload)
        
    except Exception as e:
        print(f"ERRO: Erro ao inicializar AgentOS: {e}")
        import traceback
        traceback.print_exc()

# Instância global para uso com AgentOS
aria_agentos_optimized = ARIA_SDR_AgentOS_Optimized()
app = aria_agentos_optimized.get_app()

if __name__ == "__main__":
    main()
