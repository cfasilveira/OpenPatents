import os
import sys
import subprocess
import signal
import time

processes = []

def cleanup():
    print("\n🛑 Finalizando todos os processos do MVP...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            pass
    print("👋 MVP encerrado com sucesso.")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    worker_dir = os.path.join(base_dir, "worker")
    api_dir = os.path.join(base_dir, "api")

    print("🚀 Iniciando Orquestrador do MVP OpenPatents...")

    # 1. Gerar build do Frontend
    print("\n📦 Passo 1/4: Gerando build de produção do Frontend (Vite)...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        print("✅ Build do Frontend gerada com sucesso em frontend/dist/")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao compilar o Frontend: {e}")
        sys.exit(1)

    # 2. Redefinir patentes falhas no banco
    print("\n🔄 Passo 2/4: Redefinindo patentes que falharam na base...")
    try:
        subprocess.run(["uv", "run", "python", "scripts/reset_failed.py"], cwd=worker_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Alerta: Erro ao executar reset_failed.py: {e} (Prosseguindo...)")

    # 3. Iniciar o Worker
    print("\n⚙️ Passo 3/4: Iniciando o Worker de processamento (IA)...")
    worker_proc = subprocess.Popen(["uv", "run", "python", "main.py"], cwd=worker_dir)
    processes.append(worker_proc)

    # 4. Iniciar a API FastAPI
    print("\n📡 Passo 4/4: Iniciando o Servidor API FastAPI (e Frontend integrado)...")
    api_proc = subprocess.Popen(["uv", "run", "python", "main.py"], cwd=api_dir)
    processes.append(api_proc)

    # Aguardar a inicialização da API
    time.sleep(3)

    # 5. Criar Túnel SSH Seguro para acesso externo
    print("\n🌐 Criando túnel seguro para a Web...")
    print("────────────────────────────────────────────────────────────")
    print("Aguardando conexão com localhost.run para obter a URL pública...")
    print("DICA: Quando solicitado a aceitar a chave do host, o script aceitará automaticamente.")
    print("────────────────────────────────────────────────────────────\n")

    # Comando SSH para criar o túnel reverso
    # Usando -o StrictHostKeyChecking=no para não bloquear o script
    ssh_cmd = [
        "ssh", 
        "-o", "StrictHostKeyChecking=no", 
        "-R", "80:localhost:8000", 
        "nokey@localhost.run"
    ]

    try:
        # Iniciamos o SSH e capturamos a saída padrão para ler o link gerado
        ssh_proc = subprocess.Popen(
            ssh_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1
        )
        processes.append(ssh_proc)

        # Ler as primeiras linhas do SSH até achar a URL pública gerada pelo localhost.run
        url_found = False
        start_time = time.time()
        
        while time.time() - start_time < 15:  # Timeout de 15 segundos para obter o link
            line = ssh_proc.stdout.readline()
            if not line:
                break
            print(f"[SSH Tunnel] {line.strip()}")
            if "tunneled with ssl" in line:
                # Extrair a URL
                parts = line.split()
                for part in parts:
                    if "localhost.run" in part or "lhr.life" in part:
                        # Ensure it's clean and has https:// protocol prefix
                        clean_url = part.strip().strip("[]().,")
                        if not clean_url.startswith("http"):
                            clean_url = "https://" + clean_url
                        print("\n🎉 ======================================================== 🎉")
                        print(f"🚀 MVP DISPONÍVEL NA WEB!")
                        print(f"👉 Acesse a URL: {clean_url}")
                        print("🎉 ======================================================== 🎉\n")
                        print("Pressione CTRL+C a qualquer momento para encerrar.")
                        url_found = True
                        break
                if url_found:
                    break

        if not url_found:
            print("\n⚠️ Não foi possível extrair a URL automaticamente, mas o túnel pode estar ativo.")
            print("Verifique os logs do túnel acima.")

        # Manter o processo ativo e repassar saída de logs
        while True:
            # Monitorar se algum dos subprocessos morreu
            if worker_proc.poll() is not None:
                print("❌ O processo do Worker terminou inesperadamente.")
                break
            if api_proc.poll() is not None:
                print("❌ O processo da API terminou inesperadamente.")
                break
            if ssh_proc.poll() is not None:
                print("❌ O processo do túnel SSH terminou inesperadamente.")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main()
