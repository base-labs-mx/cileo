(function () {
	'use strict';
	var p = new URLSearchParams(window.location.search);

	// Reemplazar placeholders del NDA en confidencialidad
	if (window.location.pathname.indexOf('confidencialidad') !== -1) {
		var fillValues = [p.get('orgName'), p.get('legalRep'), p.get('address')];
		document.querySelectorAll('.fill').forEach(function (el, i) {
			var val = fillValues[i];
			if (val && val.trim()) el.textContent = decodeURIComponent(val);
		});
	}

	// Modo embebido: ocultar header/footer/toc
	if (p.get('embedded') === 'true') {
		document.documentElement.classList.add('legal-embedded');
		var style = document.createElement('style');
		style.textContent =
			'.legal-embedded header,.legal-embedded footer,.legal-embedded .toc,.legal-embedded .breadcrumb-legal{display:none!important}' +
			'.legal-embedded .shell{display:block!important;max-width:100%!important;padding:0 16px 24px!important}' +
			'.legal-embedded main{max-width:none!important;padding:24px 0 40px!important;margin-top:0!important}' +
			'.legal-embedded .doc-head{margin-bottom:24px!important;padding-bottom:24px!important}' +
			'.legal-embedded body{background:#fbfcf9}';
		document.head.appendChild(style);
	}

	// Notificar scroll al padre (para modal de términos)
	if (window.parent && window.parent !== window) {
		var docKey =
			(document.querySelector('meta[name="doc-name"]') || {}).getAttribute('content') || 'unknown';
		var docEl = document.documentElement;
		window.addEventListener(
			'scroll',
			function () {
				if (docEl.scrollTop + docEl.clientHeight >= docEl.scrollHeight - 4) {
					window.parent.postMessage({ type: 'doc-scroll', key: docKey, scrolled: true }, '*');
				}
			},
			{ passive: true },
		);
	}
})();
