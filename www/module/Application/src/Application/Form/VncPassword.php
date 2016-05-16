<?php

namespace Application\Form;

use Zend\Form\Annotation;

/**
 * @Annotation\Hydrator("Zend\Stdlib\Hydrator\ObjectProperty")
 * @Annotation\Name("VncPassword")
 */
class VncPassword
{
	/**
	 * @Annotation\Type("Zend\Form\Element\Password")
	 * @Annotation\Required({"required":"true"})
	 * @Annotation\Filter({"name":"StripTags"})
	 * @Annotation\Validator({"name":"StringLength", "options":{"min":"5"}})
	 * @Annotation\Attributes({"class":"form-control", "placeholder":"Nowe hasło"})
	 * @Annotation\Options({"label":""})
	 */	
	public $password;
	
	/**
	 * @Annotation\Type("Zend\Form\Element\Submit")
	 * @Annotation\Attributes({"value":"Zmień hasło", "class":"btn btn-primary"})
	 */
	public $submit;
}
