import {
	EventDispatcher,
	Euler,
	Vector3,
	Clock
} from './three.module.js';

const _euler = new Euler( 0, 0, 0, 'YXZ' );
const _vector = new Vector3();
const clock = new Clock()
const isMobile = function () {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Fires when the user moves the mouse.
 *
 * @event PointerLockControls#change
 * @type {Object}
 */
const _changeEvent = { type: 'change' };

/**
 * Fires when the pointer lock status is "locked" (in other words: the mouse is captured).
 *
 * @event PointerLockControls#lock
 * @type {Object}
 */
const _lockEvent = { type: 'lock' };

/**
 * Fires when the pointer lock status is "unlocked" (in other words: the mouse is not captured anymore).
 *
 * @event PointerLockControls#unlock
 * @type {Object}
 */
const _unlockEvent = { type: 'unlock' };

const _MOUSE_SENSITIVITY = 0.002;
const _PI_2 = Math.PI / 2;

/**
 * The implementation of this class is based on the [Pointer Lock API](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_Lock_API).
 * `PointerLockControls` is a perfect choice for first person 3D games.
 *
 * ```js
 * const controls = new PointerLockControls( camera, document.body );
 *
 * // add event listener to show/hide a UI (e.g. the game's menu)
 * controls.addEventListener( 'lock', function () {
 *
 * 	menu.style.display = 'none';
 *
 * } );
 *
 * controls.addEventListener( 'unlock', function () {
 *
 * 	menu.style.display = 'block';
 *
 * } );
 * ```
 *
 * @augments Controls
 * @three_import import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
 */
class PCFirstPersonControls extends EventDispatcher {

	/**
	 * Constructs a new controls instance.
	 *
	 * @param {HTMLElement} masterDom - The camera master domElment.
	 * @param {Camera} camera - The camera that is managed by the controls.
	 * @param {?HTMLElement} domElement - The HTML element used for event listeners.
	 */
	constructor( masterDom, camera, domElement ) {

		super()
		this.master = masterDom
		this.object = camera;
		this.domElement = domElement

		//KeyBindAndDefine
		this.moveState = {forward: false, backward: false, left: false,
			right: false, up: false,  down: false};

		/**
		 * Whether the controls move speed.
		 *
		 * @type {number}
		 * @readonly
		 * @default 10
		 */
		this.moveSpeed = 10; // 移动速度

		/**
		 * Whether the controls are locked or not.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default false
		 */
		this.isLocked = false;

		/**
		 * Camera pitch, lower limit. Range is '[0, Math.PI]' in radians.
		 *
		 * @type {number}
		 * @default 0
		 */
		this.minPolarAngle = 0;

		/**
		 * Camera pitch, upper limit. Range is '[0, Math.PI]' in radians.
		 *
		 * @type {number}
		 * @default Math.PI
		 */
		this.maxPolarAngle = Math.PI;

		/**
		 * Multiplier for how much the pointer movement influences the camera rotation.
		 *
		 * @type {number}
		 * @default 1
		 */
		this.pointerSpeed = 0.7;


		// event listeners
		this._onMouseMove = onMouseMove.bind( this );
		this._onPointerlockChange = onPointerlockChange.bind( this );
		this._onPointerlockError = onPointerlockError.bind( this );

		this.connect();
	}

	connect() {
		this.domElement.addEventListener('click', () => {this.domElement.focus(); this.lock()});
		this.domElement.ownerDocument.addEventListener( 'mousemove', this._onMouseMove );
		this.domElement.ownerDocument.addEventListener( 'pointerlockchange', this._onPointerlockChange );
		this.domElement.ownerDocument.addEventListener( 'pointerlockerror', this._onPointerlockError );
		window.addEventListener('keydown', e => {
			if (!this.isLocked) return null
			switch (e.code) {
				case 'KeyW': this.moveState.forward = true; break;
				case 'KeyS': this.moveState.backward = true; break;
				case 'KeyA': this.moveState.left = true; break;
				case 'KeyD': this.moveState.right = true; break;
				case 'Space': this.moveState.up = true; break;
				case 'ShiftLeft': this.moveState.down = true; break;
    		}
		});
		window.addEventListener('keyup', e => {
			if (!this.isLocked) return null
			switch (e.code) {
				case 'KeyW': this.moveState.forward = false; break;
				case 'KeyS': this.moveState.backward = false; break;
				case 'KeyA': this.moveState.left = false; break;
				case 'KeyD': this.moveState.right = false; break;
				case 'Space': this.moveState.up = false; break;
				case 'ShiftLeft': this.moveState.down = false; break;
			}
		});
		setInterval( () => this.update(), 20)
	}

    update() {
		const isMoving = () => {
        	return this.moveState.forward || this.moveState.backward || 
               this.moveState.left || this.moveState.right ||
               this.moveState.up || this.moveState.down;
    	}
        if (!this.isLocked || !isMoving()) return null;

		let deltaTime = Math.min(clock.getDelta(), 0.04)
        const speed = this.moveSpeed * deltaTime;
        
        // 使用 controls 的移动方法
        if (this.moveState.forward) this.moveForward(speed);
        if (this.moveState.backward) this.moveForward(-speed);
        if (this.moveState.left) this.moveRight(-speed);
        if (this.moveState.right) this.moveRight(speed);
        
        // 垂直移动（controls 没有内置方法，需要自己处理）
        if (this.moveState.up) this.object.position.y += speed;
        if (this.moveState.down) this.object.position.y -= speed;

        // 如果有移动，请求渲染
		this.dispatchEvent( _changeEvent );
    }

	/**
	 * Returns the look direction of the camera.
	 *
	 * @param {Vector3} v - The target vector that is used to store the method's result.
	 * @return {Vector3} The normalized direction vector.
	 */
	getDirection( v ) {
		return v.set( 0, 0, - 1 ).applyQuaternion( this.object.quaternion )
	}

	/**
	 * Moves the camera forward parallel to the xz-plane. Assumes camera.up is y-up.
	 *
	 * @param {number} distance - The signed distance.
	 */
	moveForward( distance ) {
		if ( this.enabled === false ) return;

		// move forward parallel to the xz-plane
		// assumes camera.up is y-up

		const camera = this.object;
		_vector.setFromMatrixColumn( camera.matrix, 0 );
		_vector.crossVectors( camera.up, _vector );
		camera.position.addScaledVector( _vector, distance );
	}

	/**
	 * Moves the camera sidewards parallel to the xz-plane.
	 *
	 * @param {number} distance - The signed distance.
	 */
	moveRight( distance ) {
		if ( this.enabled === false ) return;

		const camera = this.object;
		_vector.setFromMatrixColumn( camera.matrix, 0 );
		camera.position.addScaledVector( _vector, distance );
	}

	/**
	 * Activates the pointer lock.
	 *
	 * @param {boolean} [unadjustedMovement=false] - Disables OS-level adjustment for mouse acceleration, and accesses raw mouse input instead.
	 * Setting it to true will disable mouse acceleration.
	 */
	lock( unadjustedMovement = false ) {
		this.domElement.requestPointerLock( {unadjustedMovement} );
	}

	/**
	 * Exits the pointer lock.
	 */
	unlock() {
		this.domElement.ownerDocument.exitPointerLock();
	}

}

// event listeners
function onMouseMove( event ) {

	if ( this.enabled === false || this.isLocked === false ) return;

	const camera = this.object;
	_euler.setFromQuaternion( camera.quaternion );

	_euler.y -= event.movementX * _MOUSE_SENSITIVITY * this.pointerSpeed;
	_euler.x -= event.movementY * _MOUSE_SENSITIVITY * this.pointerSpeed;
	_euler.x = Math.max( _PI_2 - this.maxPolarAngle, Math.min( _PI_2 - this.minPolarAngle, _euler.x ) );

	camera.quaternion.setFromEuler( _euler );
	this.dispatchEvent( _changeEvent );

}

function onPointerlockChange() {

	if ( this.domElement.ownerDocument.pointerLockElement === this.domElement ) {
		this.dispatchEvent( _lockEvent );
		this.isLocked = true;
	} else {
		this.dispatchEvent( _unlockEvent );
		this.isLocked = false;
	}

}

function onPointerlockError() {
	console.error( 'THREE.PointerLockControls: Unable to use Pointer Lock API' );
}





class PEFirstPersonControls extends EventDispatcher {

	/**
	 * Constructs a new controls instance.
	 *
	 * @param {HTMLElement} masterDom - The camera master domElment.
	 * @param {Camera} camera - The camera that is managed by the controls.
	 * @param {?HTMLElement} domElement - The HTML element used for event listeners.
	 */
	constructor( masterDom, camera, domElement ) {

		super()
		this.master = masterDom
		this.object = camera;
		this.domElement = domElement;

		//KeyBindAndDefine
		this.moveState = {plane:[0.0, 0.0], up: false,  down: false};

		/**
		 * Whether the controls move speed.
		 *
		 * @type {number}
		 * @readonly
		 * @default 10
		 */
		this.moveSpeed = 10; // 移动速度

		/**
		 * Camera pitch, lower limit. Range is '[0, Math.PI]' in radians.
		 *
		 * @type {number}
		 * @default 0
		 */
		this.minPolarAngle = 0;

		/**
		 * Camera pitch, upper limit. Range is '[0, Math.PI]' in radians.
		 *
		 * @type {number}
		 * @default Math.PI
		 */
		this.maxPolarAngle = Math.PI;

		/**
		 * Multiplier for how much the pointer movement influences the camera rotation.
		 *
		 * @type {number}
		 * @default 1
		 */
		this.pointerSpeed = 2.3;
		
		this.createPad()
		this.connect()
	}

	createPad(){
		const wrapper = this.master;
		const canvas = this.domElement
		const movePad = document.createElement('div');
		movePad.id = 'joystick';
		movePad.innerHTML = `<div id="joystick-handle"></div>`
		wrapper.appendChild(movePad);
		const verticalPad = document.createElement('div');
		verticalPad.id = 'vertical-pad';
		verticalPad.innerHTML = `
			<button data-dir="up">▲</button>
			<div style="height: 10px;"></div>
			<button data-dir="down">▼</button>`
		wrapper.appendChild(verticalPad);
		const style = document.createElement('style');
		style.textContent = `
			#joystick {
				position: absolute;
				left: 40px;
				bottom: 80px;

				width: 140px;
				height: 140px;
				border-radius: 50%;

				background: rgba(128, 128, 128, 0.4);
				touch-action: none;
				}

			#joystick-handle {
				position: absolute;
				left: 50%;
				top: 50%;

				width: 60px;
				height: 60px;
				border-radius: 50%;

				background: white;

				transform: translate(-50%, -50%);
			}
			#vertical-pad button {
				width: 60px;
				height: 60px;
				border-radius: 12px;
				border: none;
				background: rgba(0, 0, 0, 0.4);
				color: white;
				font-size: 24px;
				touch-action: none;
				user-select: none;
			}
			#vertical-pad {
				position: absolute;
				right: 30px;
				bottom: 60px;
				margin: 2% 0px;

				display: flex;
				flex-direction: column;
			gap: 12px;}`
		document.head.appendChild(style);
		canvas.style.touchAction = 'none';
	}

	connect() {
		const canvas = this.domElement
		const camera = this.object

		const joystick = document.getElementById('joystick');
		const handle = document.getElementById('joystick-handle');
		const radius = joystick.clientWidth / 2;
		const handleRadius = handle.clientWidth / 2;
		let moveTouchId = null
		let centerX = 0;
		let centerY = 0;

		let lookTouchId = null
		let lastX = 0
		let lastY = 0

		joystick.addEventListener('touchstart', e => {
  			for (const touch of e.changedTouches) {
				// 如果已经有控制视角的手指了，跳过
				if (moveTouchId !== null) break;
				e.preventDefault();

				const rect = joystick.getBoundingClientRect();
				centerX = rect.left + rect.width / 2;
				centerY = rect.top + rect.height / 2;

				moveTouchId = touch.identifier;
		}}, { passive: false });
		joystick.addEventListener('touchmove', e => {
			if (moveTouchId === null) return;

			for (const touch of e.changedTouches) {
				if (touch.identifier !== moveTouchId) continue
				const dx = touch.clientX - centerX;
				const dy = touch.clientY - centerY;

				const dist = Math.sqrt(dx * dx + dy * dy);

				let nx = dx;
				let ny = dy;

				// 超出范围 → 投影回圆周
				if (dist > radius) {
					const scale = radius / dist;
					nx *= scale;
					ny *= scale;
				}

				handle.style.transform = `translate(${nx - handleRadius}px, ${ny - handleRadius}px)`;

				// 归一化输出（-1 ~ 1）
				this.moveState.plane[0] = nx / radius;
				this.moveState.plane[1] = -ny / radius;

				e.preventDefault();
		}}, { passive: false });
		const resetJoystick = () => {
			moveTouchId = null;

			handle.style.transform = 'translate(-50%, -50%)';

			this.moveState.plane[0] = 0;
			this.moveState.plane[1] = 0;
		}
		joystick.addEventListener('touchend', resetJoystick);
		joystick.addEventListener('touchcancel', resetJoystick);


		document.querySelectorAll('button[data-dir]').forEach(btn => {
			const dir = btn.dataset.dir;
			btn.addEventListener('touchstart', e => {e.preventDefault(); this.moveState[dir] = true;});
			btn.addEventListener('touchend', e => {e.preventDefault(); this.moveState[dir] = false;});
			btn.addEventListener('touchcancel', () => {this.moveState[dir] = false;});
		});


		canvas.addEventListener('touchstart', e => {
  			for (const touch of e.changedTouches) {
				// 如果已经有控制视角的手指了，跳过
				if (lookTouchId !== null) break;

				// 如果点在 UI 上，跳过
				const isTouchOnUI = e.target.closest('#move-pad, #vertical-pad') !== null;
				if (isTouchOnUI) continue;

				lookTouchId = touch.identifier;
				lastX = touch.clientX;
				lastY = touch.clientY;
		}}, { passive: false });
		canvas.addEventListener('touchmove', e => {
			if (lookTouchId === null) return;
			for (const touch of e.changedTouches) {
				if (touch.identifier !== lookTouchId) continue;

				_euler.setFromQuaternion( camera.quaternion );
				_euler.y += (touch.clientX - lastX) * _MOUSE_SENSITIVITY * this.pointerSpeed;
				_euler.x += (touch.clientY - lastY) * _MOUSE_SENSITIVITY * this.pointerSpeed;
				_euler.x = Math.max( _PI_2 - this.maxPolarAngle, Math.min( _PI_2 - this.minPolarAngle, _euler.x ) );
				camera.quaternion.setFromEuler( _euler );

				lastX = touch.clientX;
				lastY = touch.clientY;

				e.preventDefault();
				this.dispatchEvent( _changeEvent );
  		}}, { passive: false });
		function releaseLookTouch(e) {
			for (const touch of e.changedTouches) {
				if (touch.identifier === lookTouchId) {
					lookTouchId = null;
					break;
				}
			}
		}
		canvas.addEventListener('touchend', releaseLookTouch);
		canvas.addEventListener('touchcancel', releaseLookTouch);

		setInterval( () => this.update(), 20)
	}

    update() {
		const planeMove = Math.abs(this.moveState.plane[0]) + Math.abs(this.moveState.plane[1])
		const isMoving = () => planeMove > 0.001 || this.moveState.up || this.moveState.down
        if (!isMoving()) return null;

		const deltaTime = Math.min(clock.getDelta(), 0.04)
        const moveSpeedX = this.moveSpeed * this.moveState.plane[0] * deltaTime;
        const moveSpeedY = this.moveSpeed * this.moveState.plane[1] * deltaTime;
        const riseSpeed = this.moveSpeed * deltaTime;
        
        // 使用 controls 的移动方法
        this.moveForward(moveSpeedY);
        this.moveRight(moveSpeedX);
        
        // 垂直移动（controls 没有内置方法，需要自己处理）
        if (this.moveState.up) this.object.position.y += riseSpeed;
        if (this.moveState.down) this.object.position.y -= riseSpeed;

        // 如果有移动，请求渲染
		this.dispatchEvent( _changeEvent );
    }

	/**
	 * Returns the look direction of the camera.
	 *
	 * @param {Vector3} v - The target vector that is used to store the method's result.
	 * @return {Vector3} The normalized direction vector.
	 */
	getDirection( v ) {
		return v.set( 0, 0, - 1 ).applyQuaternion( this.object.quaternion )
	}

	/**
	 * Moves the camera forward parallel to the xz-plane. Assumes camera.up is y-up.
	 *
	 * @param {number} distance - The signed distance.
	 */
	moveForward( distance ) {
		if ( this.enabled === false ) return;

		// move forward parallel to the xz-plane
		// assumes camera.up is y-up

		const camera = this.object;
		_vector.setFromMatrixColumn( camera.matrix, 0 );
		_vector.crossVectors( camera.up, _vector );
		camera.position.addScaledVector( _vector, distance );
	}

	/**
	 * Moves the camera sidewards parallel to the xz-plane.
	 *
	 * @param {number} distance - The signed distance.
	 */
	moveRight( distance ) {
		if ( this.enabled === false ) return;

		const camera = this.object;
		_vector.setFromMatrixColumn( camera.matrix, 0 );
		camera.position.addScaledVector( _vector, distance );
	}

}




/**
* Constructs a new controls instance.
*
* @param {HTMLElement} masterDom - The camera master domElment.
* @param {Camera} camera - The camera that is managed by the controls.
* @param {?HTMLElement} domElement - The HTML element used for event listeners.
*/
class FirstPersonControls {
	constructor(masterDom, camera, domElement) {
		if (!isMobile()) return new PCFirstPersonControls(masterDom, camera, domElement)
		else return new PEFirstPersonControls(masterDom, camera, domElement)
	}
}

export { PCFirstPersonControls, PEFirstPersonControls, FirstPersonControls };