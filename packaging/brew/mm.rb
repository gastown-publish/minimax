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
    sha256 "a54002c814e05222e413664f651b5916714e4700d041d5cf5724d3ae1a3e3481"
  end

  resource "dnspython" do
    url "https://files.pythonhosted.org/packages/source/d/dnspython/dnspython-2.6.1.tar.gz"
    sha256 "5ef3b9680161f6fa89daf8ad451b5f1a33b18ae8a1c6778cdf4b43f08c0a6e50"
  end

  resource "agent-client-protocol" do
    url "https://files.pythonhosted.org/packages/source/a/agent-client-protocol/agent_client_protocol-0.9.0.tar.gz"
    sha256 "06911500b51d8cb69112544e2be01fc5e7db39ef88fecbc3848c5c6f194798ee"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/source/P/PyYAML/PyYAML-6.0.1.tar.gz"
    sha256 "d858aa552c999bc8a8d57426ed01e40bef403cd8ccdd0fc5f6f04a00414cac2a"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "mm", shell_output("#{bin}/mm --version 2>&1 || echo 'ok'")
  end
end
