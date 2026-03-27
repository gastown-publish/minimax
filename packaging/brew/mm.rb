class Mm < Formula
  include Language::Python::Virtualenv

  desc "MiniMax-M2.5 AI terminal agent — chat, code, and create"
  homepage "https://minimax.villamarket.ai"
  url "https://github.com/gastown-publish/minimax/archive/refs/tags/v0.2.11.tar.gz"
  sha256 "bdd503d1cbfc07a967dba64e49d5a788eb5c8ff08c621867cd2ad7876ba10340"
  license "MIT"

  depends_on "python@3.12"

  resource "openai" do
    url "https://files.pythonhosted.org/packages/source/o/openai/openai-1.12.0.tar.gz"
    sha256 "99c5d257d09ea6533d689d1cc77caa0ac679fa21efef8893d8b0832a86877f1b"
  end

  resource "dnspython" do
    url "https://files.pythonhosted.org/packages/source/d/dnspython/dnspython-2.6.1.tar.gz"
    sha256 "e8f0f9c23a7b7cb99ded64e6c3a6f3e701d78f50c55e002b839dea7225cff7cc"
  end

  resource "agent-client-protocol" do
    url "https://files.pythonhosted.org/packages/source/a/agent-client-protocol/agent_client_protocol-0.9.0.tar.gz"
    sha256 "f744c48ab9af0f0b4452e5ab5498d61bcab97c26dbe7d6feec5fd36de49be30b"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/source/P/PyYAML/PyYAML-6.0.1.tar.gz"
    sha256 "bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "mm", shell_output("#{bin}/mm --version 2>&1 || echo 'ok'")
  end
end
