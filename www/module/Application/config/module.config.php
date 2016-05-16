<?php

return array(
    'controllers' => array(
        'invokables' => array(
            'Application\Controller\Index' => 'Application\Controller\IndexController',
            'Login' => 'Application\Controller\LoginController',
            'Panel' => 'Application\Controller\PanelController',
            'Domain' => 'Application\Controller\DomainController',
            'Hosts' => 'Application\Controller\HostsController',
        ),
    ),
    'router' => array(
        'routes' => array(
            'login' => array(
				'type' => 'Segment',
				'options' => array(
					'route' => '/login/[:action]',
					'defaults' => array(
						'controller' => 'Login',
						'action' => 'index',		
					),
					'constraints' => array(
						'controller' => 'Login',
						'action' => '[a-zA-Z]+',
					),
				),
			),
			'panel' => array(
				'type' => 'Segment',
				'options' => array(
					'route' => '/[:action]',
					'defaults' => array(
						'controller' => 'Panel',
						'action' => 'index',
					),
					'constraints' => array(
						'controller' => 'Panel',
						'action' => '[a-zA-Z]+',
					),
					
				),
			),
			'domain' => array(
				'type' => 'Segment',
				'options' => array(
					'route' => '/machine[/:action][/:name]',
					'defaults' => array(
						'controller' => 'Domain',
						'action' => 'index',
					),
					'constraints' => array(
						'controller' => 'Domain',
						'action' => '[a-zA-Z]+',
						'name' => '[a-zA-Z0-9_-]+',
					),
				),
			),
			'hosts' => array(
				'type' => 'Segment',
				'options' => array(
					'route' => '/panel/admin/hosts[/:action][/:name][/:name2]',
					'defaults' => array(
						'controller' => 'Hosts',
						'action' => 'index',
					),
					'constraints' => array(
						'controller' => 'Hosts',
						'action' => '[a-zA-Z]+',
						'name' => '[a-zA-Z0-9]+',
						'name2' => '[a-zA-Z0-9-.:_]+',
					),
				),
			),
        ),
    ),
    // Services
    'service_manager' => array(
        'abstract_factories' => array(
            'Zend\Cache\Service\StorageCacheAbstractServiceFactory',
            'Zend\Log\LoggerAbstractServiceFactory',
        ),
        'factories' => array(
			// Baza danych
            'Zend\Db\Adapter\Adapter' => 'Zend\Db\Adapter\AdapterServiceFactory',
		),
    ),
    'view_manager' => array(
        'display_not_found_reason' => true,
        'display_exceptions'       => true,
        'not_found_template'       => 'error/404',
        'exception_template'       => 'error/index',
        'template_map' => array(
            'layout/layout'           => __DIR__ . '/../view/layout/index.phtml',
            'application/index/index' => __DIR__ . '/../view/index/index.phtml',
            'error/404'               => __DIR__ . '/../view/error/404.phtml',
            'error/index'             => __DIR__ . '/../view/error/index.phtml',
        ),
        'template_path_stack' => array(
            __DIR__ . '/../view',
        ),
    ),
    // Placeholder for console routes
    'console' => array(
        'router' => array(
            'routes' => array(
            ),
        ),
    ),
);
