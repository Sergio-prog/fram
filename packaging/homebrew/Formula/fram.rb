class Fram < Formula
  include Language::Python::Virtualenv

  desc "Compact media workshop for terminal, API, and Telegram"
  homepage "https://github.com/Sergio-prog/fram"
  url "https://files.pythonhosted.org/packages/source/f/fram/fram-0.1.0.tar.gz"
  sha256 "REPLACE_WITH_PYPI_SDIST_SHA256"
  license "MIT"
  head "https://github.com/Sergio-prog/fram.git", branch: "main"

  depends_on "ffmpeg"
  depends_on "python@3.11"

  # After publishing to PyPI, generate dependency resources with:
  #   brew update-python-resources Formula/fram.rb

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Usage:", shell_output("#{bin}/fram --help")
  end
end
