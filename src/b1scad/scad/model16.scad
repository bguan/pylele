
hull() {
	union() {
		translate(v = [-1.5, -2.0, -1.0]) {
			sphere($fn = 16, r = 1);
		}
		translate(v = [-1.5, -2.0, 1.0]) {
			sphere($fn = 16, r = 1);
		}
		translate(v = [-1.5, 2.0, -1.0]) {
			sphere($fn = 16, r = 1);
		}
		translate(v = [-1.5, 2.0, 1.0]) {
			sphere($fn = 16, r = 1);
		}
		translate(v = [1.5, -2.0, -1.0]) {
			sphere($fn = 16, r = 1);
		}
		translate(v = [1.5, -2.0, 1.0]) {
			sphere($fn = 16, r = 1);
		}
		translate(v = [1.5, 2.0, -1.0]) {
			sphere($fn = 16, r = 1);
		}
		translate(v = [1.5, 2.0, 1.0]) {
			sphere($fn = 16, r = 1);
		}
	}
}
