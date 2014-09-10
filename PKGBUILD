# Maintainer: Johan Svensson <johan@loxley.se>
pkgname=halonadm
pkgver=1.0.0
pkgrel=1
pkgdesc="Manage Halon (http://halon.se) SP servers easily"
url="https://github.com/loxley/halonadm"
arch=('any')
license="GPLv2"
depends=('python3'
         'python-suds-jurko')
makedepends=('git'
             'python-setuptools')
_gitroot="https://github.com/loxley/halonadm"
_gitname="halonadm"
install='halonadm.install'

build() {
    cd "$srcdir"
    msg "Connecting to GIT server"

    if [ -d $_gitname ] ; then
        cd $_gitname && git pull origin
        msg "The local files are updated."
    else
        git clone $_gitroot $_gitname
    fi

    cd "$srcdir/$_gitname"    
    python3 setup.py build
}

package() {
    cd "$srcdir/$_gitname"
    python3 setup.py install --root="${pkgdir}" -O1
}
