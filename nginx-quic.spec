%global _disable_ld_no_undefined 1

%define nginx_home /var/lib/nginx
%define nginx_home_tmp %{nginx_home}/tmp
%define nginx_logdir /var/log/nginx
%define nginx_confdir %{_sysconfdir}/nginx
%define nginx_modulesdir %{_libdir}/nginx
%define nginx_datadir %{_datadir}/nginx
%define nginx_webroot /srv/www/html

%global optflags %{optflags} -Ofast

Summary:	Version of the NGINX web server with support for QUIC and HTTP3
Name:		nginx-quic
Version:	20230302
Release:	2
Group:		System/Servers
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:	BSD
Url:		http://nginx.net/
# hg repository at https://hg.nginx.org/nginx-quic
Source0:	https://hg.nginx.org/nginx-quic/archive/quic.tar.gz
Source1:	https://github.com/sergey-dryabzhinsky/nginx-rtmp-module/archive/refs/tags/v1.2.2-r1.tar.gz
Source51:	nginx.service
Source52:	nginx.logrotate
Source53:	virtual.conf
Source54:	ssl.conf
Source55:	nginx.conf
Source56:	php.conf
Source57:	default.conf
Source100:	index.html
Source101:	poweredby.png
Source102:	nginx-logo.png
Source103:	50x.html
Source104:	404.html

Obsoletes:	nginx < 1.24.0
BuildRequires:	gd-devel
BuildRequires:	GeoIP-devel
BuildRequires:	perl-devel
BuildRequires:	perl(ExtUtils::Embed)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(libxslt)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	systemd-macros
# For _create_ssl_certificate macro
BuildRequires:	rpm-helper
Requires:	pcre
Requires:	openssl
Provides:	webserver
Requires:	www-user
Prereq:		www-user
Requires(pre):	www-user
%systemd_requires

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev.

%package mod-http-perl
Summary:	Nginx HTTP perl module
Group:		System/Servers
Requires:	%{name} = %{EVRD}

%description mod-http-perl
%{summary}.

%package mod-http-geoip
Summary:	Nginx HTTP geoip module
Group:		System/Servers
Requires:	%{name} = %{EVRD}
Requires:	geoip

%description mod-http-geoip
%{summary}.

%package mod-http-image-filter
Summary:	Nginx HTTP image filter module
Requires:	%{name} = %{EVRD}

%description mod-http-image-filter
%{summary}.

%prep
%autosetup -p1 -n nginx-quic-quic -a 1

%build
%serverbuild_hardened
%set_build_flags

./auto/configure \
	--user=www \
	--group=www \
	--prefix=%{nginx_datadir} \
	--sbin-path=%{_sbindir}/nginx \
	--conf-path=%{nginx_confdir}/nginx.conf \
	--error-log-path=%{nginx_logdir}/error.log \
	--http-log-path=%{nginx_logdir}/access.log \
	--http-client-body-temp-path=%{nginx_home_tmp}/client_body \
	--http-proxy-temp-path=%{nginx_home_tmp}/proxy \
	--http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
	--pid-path=/run/nginx.pid \
	--lock-path=/var/lock/subsys/nginx \
	--modules-path=%{nginx_modulesdir} \
	--add-module=nginx-rtmp-module-* \
	--with-file-aio \
	--with-ipv6 \
	--with-http_ssl_module \
	--with-http_v2_module \
	--with-http_v3_module \
	--with-http_slice_module \
	--with-http_realip_module \
	--with-http_addition_module \
	--with-http_xslt_module \
	--with-http_image_filter_module=dynamic \
	--with-http_geoip_module=dynamic \
	--with-http_sub_module \
	--with-http_dav_module \
	--with-http_flv_module \
	--with-http_mp4_module \
	--with-http_gzip_static_module \
	--with-http_random_index_module \
	--with-http_secure_link_module \
	--with-http_degradation_module \
	--with-http_stub_status_module \
	--with-http_auth_request_module \
	--with-http_perl_module=dynamic \
	--with-mail \
	--with-mail_ssl_module \
	--with-pcre \
	--with-pcre-jit \
	--with-ld-opt="%{build_ldflags} -Wl,-E" # so the perl module finds its symbols

sed -i -e 's|-Wl,--no-undefined||g' objs/Makefile

# this is only passed to perl module being built and only overrides the
# default '-O' flag which anyways lowers optimizations (which we don't
# want)
%make_build OPTIMIZE="-fno-PIE"

%install
%make_install INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
find %{buildroot} -type f -exec chmod 0644 {} \;
find %{buildroot} -type f -name '*.so' -exec chmod 0755 {} \;
chmod 0755 %{buildroot}%{_sbindir}/nginx

# Install our configs...
install -p -D -m 0644 %{S:51} %{buildroot}%{_unitdir}/nginx.service
install -p -D -m 0644 %{S:52} %{buildroot}%{_sysconfdir}/logrotate.d/nginx
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
install -p -m 0644 %{S:53} %{S:54} %{buildroot}%{nginx_confdir}/conf.d
install -p -D -m 0644 %{S:55} %{buildroot}%{nginx_confdir}/
install -p -D -m 0644 %{S:55} %{buildroot}%{nginx_confdir}/nginx.conf.default
install -p -D -m 0644 %{S:56} %{buildroot}%{nginx_confdir}/
install -p -D -m 0644 %{S:56} %{buildroot}%{nginx_confdir}/php.conf.default
install -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
install -p -d -m 0755 %{buildroot}%{nginx_logdir}
install -p -d -m 0755 %{buildroot}%{nginx_webroot}
install -p -d -m 0755 %{buildroot}%{nginx_modulesdir}
install -p -d -m 0755 %{buildroot}%{nginx_datadir}/modules
mkdir -p %{buildroot}%{nginx_confdir}/sites-available %{buildroot}%{nginx_confdir}/sites-enabled
install -p -D -m 0644 %{S:57} %{buildroot}%{nginx_confdir}/sites-available/default.conf
ln -s ../sites-available/default.conf %{buildroot}%{nginx_confdir}/sites-enabled/

install -p -m 0644 %{S:100} %{S:101} %{S:102} %{S:103} %{S:104} %{buildroot}%{nginx_webroot}

# And get rid of broken upstream config samples
rm -rf %{buildroot}%{nginx_confdir}/conf.d

# add current version
sed -i -e "s|_VERSION_|%{version}|g" %{buildroot}%{nginx_webroot}/index.html

echo 'load_module "%{nginx_modulesdir}/ngx_http_perl_module.so";' > %{buildroot}%{nginx_datadir}/modules/mod-http-perl.conf
echo 'load_module "%{nginx_modulesdir}/ngx_http_geoip_module.so";' > %{buildroot}%{nginx_datadir}/modules/mod-http-geoip.conf
echo 'load_module "%{nginx_modulesdir}/ngx_http_image_filter_module.so";' > %{buildroot}%{nginx_datadir}/modules//mod-http-image-filter.conf

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-nginx.preset << EOF
enable nginx.service
EOF

%post
%systemd_post nginx.service
%_create_ssl_certificate nginx

%preun
%systemd_preun nginx.service

%postun
%systemd_postun nginx.service

%post mod-http-geoip
if [ $1 -eq 1 ]; then
    systemctl reload nginx.service >/dev/null 2>&1 || :
fi

%post mod-http-perl
if [ $1 -eq 1 ]; then
    systemctl reload nginx.service >/dev/null 2>&1 || :
fi

%post mod-http-image-filter
if [ $1 -eq 1 ]; then
    systemctl reload nginx.service >/dev/null 2>&1 || :
fi

%files
%doc README
%dir %{nginx_datadir}
%dir %{nginx_datadir}/modules
%dir %{nginx_modulesdir}
%{_sbindir}/nginx
%{_mandir}/man3/nginx.3pm*
%{_presetdir}/86-nginx.preset
%{_unitdir}/nginx.service
%{nginx_datadir}/html/*.html
/srv/www/html/*.html
/srv/www/html/*.png
%dir %{nginx_confdir}
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/nginx.conf.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config %{nginx_confdir}/fastcgi.conf.default
%config %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/nginx.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{nginx_confdir}/php.conf
%config %{nginx_confdir}/php.conf.default
%dir %{nginx_confdir}/sites-available
%config(noreplace) %{nginx_confdir}/sites-available/default.conf
%dir %{nginx_confdir}/sites-enabled
%config(noreplace) %{nginx_confdir}/sites-enabled/default.conf
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%attr(-,www,www) %dir %{nginx_home}
%attr(-,www,www) %dir %{nginx_home_tmp}
%attr(-,www,www) %dir %{nginx_logdir}

%files mod-http-perl
%{nginx_datadir}/modules/mod-http-perl.conf
%{nginx_modulesdir}/ngx_http_perl_module.so
%dir %{perl_vendorarch}/auto/nginx
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so

%files mod-http-geoip
%{nginx_datadir}/modules/mod-http-geoip.conf
%{nginx_modulesdir}/ngx_http_geoip_module.so

%files mod-http-image-filter
%{nginx_datadir}/modules/mod-http-image-filter.conf
%{nginx_modulesdir}/ngx_http_image_filter_module.so
