class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/18/a7/31d112a7197a1c5fa15f51a02f56c448400919add78930afdfe9251b4f85/trmd-0.1.17.tar.gz"
  sha256 "f916abf278d8e03daaf70fde0f80b23571569c221c64f2694f683595155466db"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
