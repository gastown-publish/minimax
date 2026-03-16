class Mm < Formula
  include Language::Python::Virtualenv

  desc "MiniMax-M2.5 AI terminal agent — chat, code, and create"
  homepage "https://minimax.villamarket.ai"
  url "https://github.com/gastown-publish/minimax/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "" # TODO: fill after release
  license "MIT"

  depends_on "python@3.12"

  resource "click" do
    url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.8.tar.gz"
    sha256 "ed53c9d8990d83c2a27deae68e4ee337473f6330c040a31d4225c9574d0a19e5"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/b1/df/48c586a5fe32a0f01c5f51f69aa7d516f0c54d5f0a3a35644a6087e1c37f/httpx-0.28.1.tar.gz"
    sha256 "75e98c5f16b0f35b567856f928611f4c9e2f0f4c9d24a0b72efa8fa9e999c398"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/a1/53/830aa4c3066a8ab0ae9a9955976fb770f9a8e9c2c3a0e807596c5286bf9e/rich-13.9.4.tar.gz"
    sha256 "439594978a49a09530cff7ebc4b5c7103ef57c74372e76ab55c5b36be20b4328"
  end

  resource "openai" do
    url "https://files.pythonhosted.org/packages/source/o/openai/openai-1.82.0.tar.gz"
    sha256 "" # TODO: fill with actual hash
  end

  resource "dnspython" do
    url "https://files.pythonhosted.org/packages/source/d/dnspython/dnspython-2.7.0.tar.gz"
    sha256 "" # TODO: fill with actual hash
  end

  resource "agent-client-protocol" do
    url "https://files.pythonhosted.org/packages/source/a/agent-client-protocol/agent_client_protocol-0.8.1.tar.gz"
    sha256 "" # TODO: fill with actual hash
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/source/P/PyYAML/pyyaml-6.0.2.tar.gz"
    sha256 "" # TODO: fill with actual hash
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "mm, version", shell_output("#{bin}/mm --version")
    assert_match "Bundled Skills", shell_output("#{bin}/mm skills list")
  end
end
