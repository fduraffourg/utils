use std::rand::{task_rng, Rng};
use std::fmt;
use std::num::abs;

/* Game structure */
struct Game {
    total: int,
    values: Vec<int>
}

impl fmt::Show for Game {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "<Total: {} with {}>", self.total, self.values)
    }
}

/* Solution structure */ 
#[deriving(Clone)]
struct Solution {
    total: int,
    calcul: String
}

impl fmt::Show for Solution {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "<Total: {}, Calcul: {}>", self.total, self.calcul)
    }
}


fn main() {
    let game = generate_new_game();
    println!("New game: {}", game);
    let solution = solve_game(game);
    println!("Solution: {}", solution);

}

fn generate_new_game() -> Game {
    let choices = [1i, 2i, 3i, 4i, 5i, 6i, 7i, 8i, 9i, 10i, 25i, 50i, 75i, 100i];

    let mut rng = task_rng();

    let mut values : Vec<int> = Vec::new();
    for _ in range(0u, 6) {
        values.push(choices[rng.gen_range(0, choices.len())]);
    }

    Game{total: rng.gen_range(100i, 999i),
        values: values}
}

fn solve_game(game: Game) -> Solution {
    best_sub_solution(game.total, Solution{total: 0, calcul: format!("0")}, game.values)
}

fn best_sub_solution(total: int, solution : Solution, left_values : Vec<int>) -> Solution {
    if solution.total == total {
        return solution
    }

    if left_values.len() <= 0 {
        return solution
    }

    let mut best_solution = solution.clone();
    let keep_best = |s: Solution| -> () {
        if abs(s.total - total) < abs(best_solution.total - total) {
            best_solution = s.clone();
        }
    };

    let mut solutions : Vec<Solution> = Vec::new();

    for i in range(0, left_values.len()) {
        let mut values = left_values.clone();
        let value = values.remove(i).unwrap();

        keep_best(best_sub_solution(total,
                                        Solution{ total: solution.total + value,
                                                  calcul: format!("( {} + {} )", solution.calcul, value)},
                                        values.clone()));

        keep_best(best_sub_solution(total,
                                         Solution{ total: solution.total * value,
                                             calcul: format!("( {} x {} )", solution.calcul, value)},
                                         values.clone()));

        if total > value {
            keep_best(best_sub_solution(total,
                                        Solution{ total: solution.total - value,
                                                  calcul: format!("( {} - {} )", solution.calcul, value)},
                                        values.clone()));
        }

        if value > total {
            keep_best(best_sub_solution(total,
                                        Solution{ total: value - solution.total,
                                                  calcul: format!("( {} - {} )", value, solution.calcul)},
                                        values.clone()));
        }

        if total % value == 0 {
            keep_best(best_sub_solution(total,
                                        Solution{ total: solution.total / value,
                                                  calcul: format!("( {} / {} )", solution.calcul, value)},
                                        values.clone()));
        }

        if value % total == 0 {
            keep_best(best_sub_solution(total,
                                        Solution{ total: value / solution.total,
                                                  calcul: format!("( {} / {} )", value, solution.calcul)},
                                        values.clone()));
        }
    }

     //Solution{
     //    total: (*best_solution).total,
     //    calcul: (*best_solution).calcul.clone()}
     best_solution.clone()
}
