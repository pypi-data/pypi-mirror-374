class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/04/5f/9f8840c5b8261fb2552f884c097618b605881735ded308b03cd96a083c7c/age_mcp_server-0.2.23.tar.gz"
  sha256 "4e4af5d49d130def72881862bc65838e55475f327b3370e635965fed6c54b3a9"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/4d/42/70415f1a0b954d9223a67dfb0c3b3426c0c461eb14ce9ac80ff13c2a13ee/agefreighter-1.0.12.tar.gz"
    sha256 "6413a4c54bc7a6aea65357fef40a41fc6967c855929e4ac3ee11f564e6df30d5"
  end

  resource "ply" do
    url "https://files.pythonhosted.org/packages/e5/69/882ee5c9d017149285cab114ebeab373308ef0f874fcdac9beb90e0ac4da/ply-3.11.tar.gz"
    sha256 "00c7c1aaa88358b9c765b6d3000c6eec0ba42abca5351b095321aef446081da3"
  end

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "psycopg[binary,pool]", "mcp"
  end

  test do
    system "#{bin}/age-mcp-server", "--help"
  end
end
