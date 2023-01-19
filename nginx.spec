%global _disable_ld_no_undefined 1

%define nginx_user nginx
%define nginx_group %{nginx_user}
%define nginx_home /var/lib/nginx
%define nginx_home_tmp %{nginx_home}/tmp
%define nginx_logdir /var/log/nginx
%define nginx_confdir %{_sysconfdir}/nginx
%define nginx_modulesdir %{_libdir}/nginx
%define nginx_datadir %{_datadir}/nginx
%define nginx_webroot /srv/www/html

%global optflags %{optflags} -Ofast

Summary:	Robust, small and high performance HTTP and reverse proxy server
Name:		nginx
Version:	1.23.3
Release:	1
Group:		System/Servers
# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:	BSD
Url:		http://nginx.net/
Source0:	http://nginx.org/download/%{name}-%{version}.tar.gz
Source1:	nginx.sysusers
Source2:	nginx.service
Source3:	nginx.logrotate
Source4:	virtual.conf
Source5:	ssl.conf
Source6:	nginx.conf
Source7:	php.conf
Source100:	index.html
Source101:	poweredby.png
Source102:	nginx-logo.png
Source103:	50x.html
Source104:	404.html
Patch0:		nginx-1.15.2-enable-ipv6.patch

BuildRequires:	gd-devel
BuildRequires:	GeoIP-devel
BuildRequires:	perl-devel
BuildRequires:	perl(ExtUtils::Embed)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(libxslt)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	systemd-macros
Requires:	pcre
Requires:	openssl
Provides:	webserver
%systemd_requires

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev.

%package mod-http-perl
Summary:	Nginx HTTP perl module
Group:		System/Servers
Requires:	%{name}

%description mod-http-perl
%{summary}.

%package mod-http-geoip
Summary:	Nginx HTTP geoip module
Group:		System/Servers
Requires:	%{name}
Requires:	geoip

%description mod-http-geoip
%{summary}.

%package mod-http-image-filter
Summary:	Nginx HTTP image filter module
Requires:	%{name}

%description mod-http-image-filter
%{summary}.

%prep
%autosetup -p1

%build
%serverbuild_hardened
%set_build_flags

./configure \
	--user=%{nginx_user} \
	--group=%{nginx_group} \
	--prefix=%{nginx_datadir} \
	--sbin-path=%{_sbindir}/%{name} \
	--conf-path=%{nginx_confdir}/%{name}.conf \
	--error-log-path=%{nginx_logdir}/error.log \
	--http-log-path=%{nginx_logdir}/access.log \
	--http-client-body-temp-path=%{nginx_home_tmp}/client_body \
	--http-proxy-temp-path=%{nginx_home_tmp}/proxy \
	--http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
	--pid-path=/run/%{name}.pid \
	--lock-path=/var/lock/subsys/%{name} \
	--modules-path=%{nginx_modulesdir} \
	--with-file-aio \
	--with-ipv6 \
	--with-http_ssl_module \
	--with-http_v2_module \
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

install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/nginx.service
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
install -p -m 0644 %{SOURCE4} %{SOURCE5} %{buildroot}%{nginx_confdir}/conf.d
install -p -D -m 0644 %{SOURCE6} %{buildroot}%{nginx_confdir}/
install -p -D -m 0644 %{SOURCE7} %{buildroot}%{nginx_confdir}/
install -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
install -p -d -m 0755 %{buildroot}%{nginx_logdir}
install -p -d -m 0755 %{buildroot}%{nginx_webroot}
install -p -d -m 0755 %{buildroot}%{nginx_modulesdir}
install -p -d -m 0755 %{buildroot}%{nginx_datadir}/modules
mkdir -p %{buildroot}%{nginx_confdir}/sites-available %{buildroot}%{nginx_confdir}/sites-enabled

install -p -m 0644 %{SOURCE100} %{SOURCE101} %{SOURCE102} %{SOURCE103} %{SOURCE104} %{buildroot}%{nginx_webroot}

# add current version
sed -i -e "s|_VERSION_|%{version}|g" %{buildroot}%{nginx_webroot}/index.html

install -d %{buildroot}%{_mandir}/man8
install -m0644 man/*.8 %{buildroot}%{_mandir}/man8/

echo 'load_module "%{nginx_modulesdir}/ngx_http_perl_module.so";' > %{buildroot}%{nginx_datadir}/modules/mod-http-perl.conf
echo 'load_module "%{nginx_modulesdir}/ngx_http_geoip_module.so";' > %{buildroot}%{nginx_datadir}/modules/mod-http-geoip.conf
echo 'load_module "%{nginx_modulesdir}/ngx_http_image_filter_module.so";' > %{buildroot}%{nginx_datadir}/modules//mod-http-image-filter.conf

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-nginx.preset << EOF
enable nginx.service
EOF

%post
%systemd_post nginx.service

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
%doc LICENSE CHANGES README
%dir %{nginx_datadir}
%dir %{nginx_datadir}/modules
%dir %{nginx_modulesdir}
%{_sbindir}/%{name}
%{_mandir}/man3/%{name}.3pm*
%{_mandir}/man8/*
%{_sysusersdir}/%{name}.conf
%{_presetdir}/86-nginx.preset
%{_unitdir}/nginx.service
%{nginx_datadir}/html/*.html
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%config(noreplace) %{nginx_confdir}/conf.d/*.conf
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/%{name}.conf.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config %{nginx_confdir}/fastcgi.conf.default
%config %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/%{name}.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config %{nginx_confdir}/php.conf
%dir %{nginx_confdir}/sites-available
%dir %{nginx_confdir}/sites-enabled
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_logdir}
/srv/www

%files mod-http-perl
%{nginx_datadir}/modules/mod-http-perl.conf
%{nginx_modulesdir}/ngx_http_perl_module.so
%dir %{perl_vendorarch}/auto/%{name}
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so

%files mod-http-geoip
%{nginx_datadir}/modules/mod-http-geoip.conf
%{nginx_modulesdir}/ngx_http_geoip_module.so

%files mod-http-image-filter
%{nginx_datadir}/modules/mod-http-image-filter.conf
%{nginx_modulesdir}/ngx_http_image_filter_module.so
